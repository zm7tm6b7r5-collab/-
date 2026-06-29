import React from 'react';
import ProgressRing from './ProgressRing';

function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

export default function TimerDisplay({ remaining, total, mode, status }) {
  const progress = total > 0 ? remaining / total : 1;
  const color = mode === 'work' ? 'var(--color-work)' : 'var(--color-break)';
  const label = mode === 'work' ? '专注' : '休息';

  return (
    <div className="timer-display">
      <div className="ring-container">
        <ProgressRing progress={progress} color={color} />
        <div className="timer-text">
          <span className="timer-mode" style={{ color }}>{label}</span>
          <span className="timer-time">{formatTime(remaining)}</span>
          <span className="timer-status">
            {status === 'idle' ? '准备开始' : status === 'paused' ? '已暂停' : ''}
          </span>
        </div>
      </div>
    </div>
  );
}
