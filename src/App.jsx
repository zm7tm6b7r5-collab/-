import React, { useCallback } from 'react';
import useTimer from './hooks/useTimer';
import TimerDisplay from './components/TimerDisplay';
import Controls from './components/Controls';

const WORK_SECONDS = 25 * 60;
const BREAK_SECONDS = 5 * 60;

function playBeep() {
  const ctx = new (window.AudioContext || window.webkitAudioContext)();
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.connect(gain);
  gain.connect(ctx.destination);
  osc.frequency.value = 880;
  osc.type = 'sine';
  gain.gain.setValueAtTime(0.3, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.3);
  osc.start(ctx.currentTime);
  osc.stop(ctx.currentTime + 0.3);
}

function notify(title, body) {
  if (window.electronAPI) {
    window.electronAPI.sendNotification(title, body);
  } else if ('Notification' in window && Notification.permission === 'granted') {
    new Notification(title, { body });
  }
}

export default function App() {
  const timer = useTimer();
  const totalSeconds = timer.mode === 'work' ? WORK_SECONDS : BREAK_SECONDS;

  const handleComplete = useCallback((mode) => {
    playBeep();
    const title = mode === 'break' ? '休息时间结束' : '工作时间结束';
    const body = mode === 'break' ? '开始下一轮专注吧！' : '休息一下吧！';
    notify(title, body);
  }, []);

  timer.onComplete(handleComplete);

  return (
    <div className="app">
      <TimerDisplay
        remaining={timer.remaining}
        total={totalSeconds}
        mode={timer.mode}
        status={timer.status}
      />
      <Controls
        status={timer.status}
        onStart={timer.start}
        onPause={timer.pause}
        onReset={timer.reset}
      />
    </div>
  );
}
