from __future__ import annotations

import sys
import time
import queue
import threading
from dataclasses import dataclass
from typing import Optional, Literal, Callable, Dict, Any


try:
    import pyttsx3  # type: ignore
except Exception:
    pyttsx3 = None  # fallback mode


Severity = Literal["info", "warning", "error"]


@dataclass
class SpeakResult:
    ok: bool
    text: str
    severity: Severity
    engine_used: str
    error: Optional[str] = None
    timestamp: float = 0.0


@dataclass
class _TTSJob:
    text: str
    severity: Severity
    created_at: float
    done_event: threading.Event
    result_holder: Dict[str, Any]  # stores SpeakResult for blocking calls


class TTSFeedbackEngine:
    """
    Module 5: Text-to-Speech Feedback Engine

    Design goals:
    - No system crash on TTS failure (fallback to console logging)
    - Blocking playback supported (default for confirmations)
    - Optional non-blocking playback supported (queue + worker)
    - Minimal external dependencies (pyttsx3 only; offline)
    """

    def __init__(
        self,
        rate: int = 175,
        volume: float = 1.0,
        voice_name_contains: Optional[str] = None,
        logger: Optional[Callable[[str, Severity], None]] = None,
        enable_async_worker: bool = True,
    ):
        """
        Args:
            rate: speech rate (pyttsx3)
            volume: 0.0 to 1.0
            voice_name_contains: optional substring to select a voice
            logger: optional (message, severity) logging callback
            enable_async_worker: if True, allows non-blocking speaks via queue
        """
        self._logger = logger
        self._rate = rate
        self._volume = max(0.0, min(1.0, float(volume)))
        self._voice_name_contains = voice_name_contains

        self._engine = None
        self._engine_ok = False
        self._engine_name = "pyttsx3" if pyttsx3 is not None else "fallback"

        # Async queue/worker for non-blocking playback
        self._enable_async_worker = enable_async_worker
        self._q: "queue.Queue[_TTSJob]" = queue.Queue()
        self._stop = threading.Event()
        self._worker: Optional[threading.Thread] = None

        # A lock to prevent overlapping runAndWait calls (thread safety)
        self._speak_lock = threading.Lock()

        self._init_engine()

        if self._enable_async_worker:
            self._worker = threading.Thread(target=self._worker_loop, daemon=True)
            self._worker.start()

    # Public API 

    def speak(self, text: str, severity: Severity = "info", blocking: bool = True) -> SpeakResult:
        """
        Speak a text message.

        - blocking=True: speaks immediately (or via engine) and waits until finished.
        - blocking=False: enqueues message (if async worker enabled) and returns immediately.

        Returns SpeakResult with success/failure and fallback info.
        """
        text_clean = self._validate_text(text)
        if text_clean is None:
            return SpeakResult(
                ok=False,
                text=str(text or ""),
                severity=severity,
                engine_used="none",
                error="Empty text not allowed",
                timestamp=time.time(),
            )

        if blocking or not self._enable_async_worker:
            # Direct speak in caller thread
            return self._speak_blocking(text_clean, severity)

        # Non-blocking: enqueue job
        done = threading.Event()
        holder: Dict[str, Any] = {}
        job = _TTSJob(
            text=text_clean,
            severity=severity,
            created_at=time.time(),
            done_event=done,
            result_holder=holder,
        )
        self._q.put(job)

        # Return immediate result (accepted)
        return SpeakResult(
            ok=True,
            text=text_clean,
            severity=severity,
            engine_used=self._engine_name,
            error=None,
            timestamp=time.time(),
        )

    def speak_success(self, text: str, blocking: bool = True) -> SpeakResult:
        """Convenience for success confirmations."""
        return self.speak(text, severity="info", blocking=blocking)

    def speak_warning(self, text: str, blocking: bool = True) -> SpeakResult:
        """Convenience for warning messages."""
        return self.speak(text, severity="warning", blocking=blocking)

    def speak_error(self, text: str, blocking: bool = True) -> SpeakResult:
        """Convenience for error messages."""
        return self.speak(text, severity="error", blocking=blocking)

    def configure(self, *, rate: Optional[int] = None, volume: Optional[float] = None) -> None:
        """
        Update rate/volume without affecting other modules.
        Safe to call at runtime.
        """
        if rate is not None:
            self._rate = int(rate)
        if volume is not None:
            self._volume = max(0.0, min(1.0, float(volume)))

        if self._engine_ok and self._engine is not None:
            try:
                self._engine.setProperty("rate", self._rate)
                self._engine.setProperty("volume", self._volume)
                self._log(f"TTS reconfigured: rate={self._rate}, volume={self._volume}", "info")
            except Exception as e:
                self._log(f"TTS configure failed: {e}", "error")

    def set_voice(self, voice_name_contains: Optional[str]) -> bool:
        """
        Attempt to set voice by substring match.
        Returns True on success.
        """
        self._voice_name_contains = voice_name_contains
        if not (self._engine_ok and self._engine is not None):
            self._log("Cannot set voice: engine not available.", "warning")
            return False
        try:
            voices = self._engine.getProperty("voices") or []
            if not voice_name_contains:
                self._log("Voice selection cleared (default voice).", "info")
                return True

            sub = voice_name_contains.lower()
            chosen = None
            for v in voices:
                name = (getattr(v, "name", "") or "").lower()
                if sub in name:
                    chosen = getattr(v, "id", None)
                    break

            if chosen:
                self._engine.setProperty("voice", chosen)
                self._log(f"Voice set using match: {voice_name_contains}", "info")
                return True

            self._log(f"No voice matched: {voice_name_contains}", "warning")
            return False
        except Exception as e:
            self._log(f"Set voice failed: {e}", "error")
            return False

    def flush(self, timeout: float = 10.0) -> bool:
        """
        If using async mode, wait until queue is empty or timeout.
        Returns True if queue drained.
        """
        if not self._enable_async_worker:
            return True
        start = time.time()
        while time.time() - start < timeout:
            if self._q.empty():
                return True
            time.sleep(0.05)
        return False

    def shutdown(self) -> None:
        """
        Stop worker and release audio resources.
        Safe to call multiple times.
        """
        try:
            self._stop.set()
            if self._enable_async_worker:
                # Unblock queue get
                self._q.put(_TTSJob(text="__STOP__", severity="info", created_at=time.time(),
                                   done_event=threading.Event(), result_holder={}))
            if self._worker is not None:
                self._worker.join(timeout=2.0)
        except Exception:
            pass

        try:
            if self._engine_ok and self._engine is not None:
                self._engine.stop()
        except Exception:
            pass

        self._log("TTS engine shutdown complete.", "info")

    # Internal Engine 

    def _init_engine(self) -> None:
        """
        Initialize pyttsx3 engine (offline) per SRS.
        If init fails, remain in fallback mode (prints/logs only).
        """
        if pyttsx3 is None:
            self._engine_ok = False
            self._engine = None
            self._engine_name = "fallback"
            self._log("pyttsx3 not available; using fallback console output only.", "error")
            return

        try:
            eng = pyttsx3.init()
            eng.setProperty("rate", self._rate)
            eng.setProperty("volume", self._volume)

            # Optional voice selection
            if self._voice_name_contains:
                self._select_voice(eng, self._voice_name_contains)

            self._engine = eng
            self._engine_ok = True
            self._engine_name = "pyttsx3"
            self._log("pyttsx3 initialized successfully (offline TTS ready).", "info")
        except Exception as e:
            self._engine_ok = False
            self._engine = None
            self._engine_name = "fallback"
            self._log(f"TTS init failed: {e}. Using fallback console output only.", "error")

    def _select_voice(self, eng, voice_name_contains: str) -> None:
        try:
            voices = eng.getProperty("voices") or []
            sub = voice_name_contains.lower()
            for v in voices:
                name = (getattr(v, "name", "") or "").lower()
                if sub in name:
                    vid = getattr(v, "id", None)
                    if vid:
                        eng.setProperty("voice", vid)
                        self._log(f"Voice matched and set: {voice_name_contains}", "info")
                        return
            self._log(f"Voice match not found: {voice_name_contains} (using default).", "warning")
        except Exception as e:
            self._log(f"Voice selection failed: {e} (using default).", "warning")

    #Speaking Paths 

    def _speak_blocking(self, text: str, severity: Severity) -> SpeakResult:
        """
        Blocking speak: speak immediately and return final result.
        Must never crash the system.
        """
        ts = time.time()
        self._log(f"TTS[{severity}]: {text}", severity)

        if not (self._engine_ok and self._engine is not None):
            # Fallback mode: print only
            self._fallback_output(text, severity)
            return SpeakResult(
                ok=False,
                text=text,
                severity=severity,
                engine_used="fallback",
                error="TTS engine unavailable; fallback used",
                timestamp=ts,
            )

        try:
            # Prevent overlapping engine access
            with self._speak_lock:
                self._engine.say(text)
                self._engine.runAndWait()
            return SpeakResult(
                ok=True,
                text=text,
                severity=severity,
                engine_used="pyttsx3",
                error=None,
                timestamp=ts,
            )
        except Exception as e:
            # Graceful degrade: mark engine unusable and fallback
            self._engine_ok = False
            self._log(f"TTS playback failed: {e}. Switching to fallback output.", "error")
            self._fallback_output(text, severity)
            return SpeakResult(
                ok=False,
                text=text,
                severity=severity,
                engine_used="fallback",
                error=str(e),
                timestamp=ts,
            )

    def _worker_loop(self) -> None:
        """
        Non-blocking playback support: sequential worker that speaks queued messages.
        Prevents overlap and avoids crashing system.
        """
        while not self._stop.is_set():
            try:
                job = self._q.get(timeout=0.2)
            except queue.Empty:
                continue
            except Exception:
                continue

            if job.text == "__STOP__":
                break

            # Speak and store result for completeness (even though caller already returned)
            res = self._speak_blocking(job.text, job.severity)
            job.result_holder["result"] = res
            job.done_event.set()

    # Utilitie

    def _validate_text(self, text: str) -> Optional[str]:
        if text is None:
            self._log("TTS validation failed: text is None", "warning")
            return None
        s = str(text).strip()
        if not s:
            self._log("TTS validation failed: empty text", "warning")
            return None
        return s

    def _fallback_output(self, text: str, severity: Severity) -> None:
       
        out = sys.stderr if severity == "error" else sys.stdout
        try:
            out.write(f"[TTS-FALLBACK/{severity.upper()}] {text}\n")
            out.flush()
        except Exception:
            # Last resort: ignore
            pass

    def _log(self, message: str, severity: Severity) -> None:
        """
        Logging with timestamps + severity.
        Integrates with centralized logging if logger callback is provided.
        """
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        line = f"{ts} [{severity.upper()}] {message}"

        if self._logger is not None:
            try:
                self._logger(line, severity)
                return
            except Exception:
                # If external logger fails, fallback to print
                pass

        # Default console logging
        stream = sys.stderr if severity == "error" else sys.stdout
        try:
            stream.write(line + "\n")
            stream.flush()
        except Exception:
            pass


#  Demo

def _demo():
    """
    Standalone demo for Module 5.
    Run:
        python module5_tts.py
    """
    tts = TTSFeedbackEngine(rate=175, volume=1.0, enable_async_worker=True)

    # Blocking (confirmations)
    tts.speak_success("Hello Shoaib. Module five is running.", blocking=True)
    tts.speak_success("Opening Notepad.", blocking=True)

    # Non-blocking (continuous interaction)
    tts.speak_warning("This is a warning message (non-blocking).", blocking=False)
    tts.speak_error("This is an error message (non-blocking).", blocking=False)

    # Wait for queue to drain
    tts.flush(timeout=5.0)

    # Shutdown cleanly
    tts.shutdown()


if __name__ == "__main__":
    _demo()
