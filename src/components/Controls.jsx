import React from 'react';

export default function Controls({ status, onStart, onPause, onReset }) {
  return (
    <div className="controls">
      {status === 'running' ? (
        <button className="btn btn-pause" onClick={onPause}>
          暂停
        </button>
      ) : (
        <button className="btn btn-start" onClick={onStart}>
          {status === 'paused' ? '继续' : '开始'}
        </button>
      )}
      <button
        className="btn btn-reset"
        onClick={onReset}
        disabled={status === 'idle'}
      >
        重置
      </button>
    </div>
  );
}
