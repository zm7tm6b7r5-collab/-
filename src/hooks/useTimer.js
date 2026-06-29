import { useReducer, useEffect, useRef, useCallback } from 'react';

const WORK_SECONDS = 25 * 60;
const BREAK_SECONDS = 5 * 60;

const initialState = {
  status: 'idle', // idle | running | paused
  mode: 'work',   // work | break
  remaining: WORK_SECONDS,
};

function reducer(state, action) {
  switch (action.type) {
    case 'TICK':
      if (state.remaining <= 1) {
        const nextMode = state.mode === 'work' ? 'break' : 'work';
        return {
          ...state,
          mode: nextMode,
          remaining: nextMode === 'work' ? WORK_SECONDS : BREAK_SECONDS,
          status: 'idle',
        };
      }
      return { ...state, remaining: state.remaining - 1 };

    case 'START':
      return { ...state, status: 'running' };

    case 'PAUSE':
      return { ...state, status: 'paused' };

    case 'RESET':
      return {
        ...state,
        status: 'idle',
        mode: 'work',
        remaining: WORK_SECONDS,
      };

    default:
      return state;
  }
}

export default function useTimer() {
  const [state, dispatch] = useReducer(reducer, initialState);
  const intervalRef = useRef(null);
  const onCompleteRef = useRef(null);

  const tick = useCallback(() => dispatch({ type: 'TICK' }), []);

  useEffect(() => {
    if (state.status === 'running') {
      intervalRef.current = setInterval(tick, 1000);
    } else {
      clearInterval(intervalRef.current);
    }
    return () => clearInterval(intervalRef.current);
  }, [state.status, tick]);

  // Detect completion (status goes from running to idle)
  const prevRemainingRef = useRef(state.remaining);
  useEffect(() => {
    if (
      prevRemainingRef.current === 1 &&
      state.remaining !== 1 &&
      state.status === 'idle' &&
      onCompleteRef.current
    ) {
      onCompleteRef.current(state.mode);
    }
    prevRemainingRef.current = state.remaining;
  }, [state.remaining, state.status, state.mode]);

  const start = useCallback(() => dispatch({ type: 'START' }), []);
  const pause = useCallback(() => dispatch({ type: 'PAUSE' }), []);
  const reset = useCallback(() => dispatch({ type: 'RESET' }), []);
  const onComplete = useCallback((fn) => {
    onCompleteRef.current = fn;
  }, []);

  return { ...state, start, pause, reset, onComplete };
}
