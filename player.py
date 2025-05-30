import keyboard
import mouse
import time
import threading
import random
import logging # 로깅 추가
import psutil # 메모리 사용량 측정을 위해 psutil 임포트
import os     # 현재 프로세스 ID 얻기 위해 os 임포트
import gc     # 가비지 컬렉션 임포트

# --- 메모리 로깅 함수 추가 (gesture_manager.py와 동일) ---
def log_memory_usage(label):
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / (1024 * 1024) # RSS를 MB 단위로
    logging.info(f"[Memory Check][{label}] 사용량: {memory_mb:.2f} MB")
# --- 함수 추가 끝 ---

class MacroPlayer:
    def __init__(self):
        self.playing = False
        self.stop_requested = False
        self.play_thread = None
        self.base_x = 0 # 상대 이동 기준 X
        self.base_y = 0 # 상대 이동 기준 Y
    
    def play_macro(self, events, repeat_count=1, base_x=None, base_y=None):
        """매크로 실행 (선택적 기준 좌표 포함)"""
        if self.playing:
            print("이미 매크로가 실행 중입니다.")
            return False
        
        # 상대 이동 기준 좌표 설정
        if base_x is not None and base_y is not None:
            self.base_x, self.base_y = base_x, base_y
            print(f"제공된 기준 좌표 사용: ({self.base_x}, {self.base_y})")
        else:
            # 기준 좌표가 없으면 현재 마우스 위치 사용
            current_pos = mouse.get_position()
            self.base_x, self.base_y = current_pos
            print(f"현재 마우스 위치를 기준 좌표로 사용: ({self.base_x}, {self.base_y})")
        
        # 매크로 실행 스레드 시작
        self.stop_requested = False
        thread_start_req_time = time.time()
        print(f"[TimeLog] Requesting thread start at: {thread_start_req_time:.3f}")

        # --- 이전 스레드 종료 대기 --- (추가)
        if self.play_thread and self.play_thread.is_alive():
            logging.info(f"[Thread Check] 이전 매크로 재생 스레드({self.play_thread.ident}) 종료 대기 중...")
            self.play_thread.join() # 이전 스레드가 끝날 때까지 기다림
            logging.info(f"[Thread Check] 이전 매크로 재생 스레드 종료 완료.")
        # --- 대기 끝 ---

        # 스레드에 이벤트와 반복 횟수 전달
        self.play_thread = threading.Thread(target=self._play_events, args=(events, repeat_count))
        # self.play_thread.daemon = True # 데몬 스레드 설정 제거
        logging.info(f"[Thread Check] 스레드 시작 전 활성 스레드 수: {threading.active_count()}") # 스레드 수 로그
        self.play_thread.start()
        thread_started_time = time.time() # 스레드 start() 호출 직후
        print(f"[TimeLog] Thread start method returned at: {thread_started_time:.3f} (overhead: {thread_started_time - thread_start_req_time:.3f}s)")
        
        return True
    
    def stop_playing(self):
        """매크로 실행 중지"""
        if not self.playing:
            return False
        
        self.stop_requested = True
        if self.play_thread and self.play_thread.is_alive():
            self.play_thread.join(timeout=1.0)
            
        print("매크로 실행이 중지되었습니다.")
        self.playing = False # 상태 명시적 업데이트
        return True
    
    def _play_events(self, events, repeat_count):
        """실제 이벤트 실행 (내부 메소드)"""
        thread_actual_start_time = time.time()
        self.playing = True
        logging.info(f"[Thread Check] 매크로 재생 스레드 시작. 활성 스레드 수: {threading.active_count()}") # 스레드 수 로그
        print(f"[TimeLog] Play thread actually started execution at: {thread_actual_start_time:.3f}")
        print(f"매크로 실행 시작 (반복 횟수: {repeat_count if repeat_count > 0 else '무한'})")
        # 스레드 시작 시 사용될 기준 좌표 로깅
        print(f"상대 이동 기준 좌표: ({self.base_x}, {self.base_y})")
        
        try:
            sort_start_time = time.time()
            sorted_events = sorted(events, key=lambda x: x['time'])
            sort_end_time = time.time()
            print(f"[TimeLog] Sorted events at: {sort_end_time:.3f} (took {sort_end_time - sort_start_time:.3f}s)")
            
            current_repeat = 0
            while (repeat_count == 0 or current_repeat < repeat_count) and not self.stop_requested:
                current_repeat += 1
                print(f"반복 {current_repeat}{' / ' + str(repeat_count) if repeat_count > 0 else ''}")
                
                loop_start_time = time.time() # 루프 시작 시간 (매 반복마다)
                print(f"[TimeLog] Repeat {current_repeat} started at: {loop_start_time:.3f}")
                
                for i, event in enumerate(sorted_events):
                    if self.stop_requested:
                        break
                    
                    event_type = event['type']
                    event_exec_start_time = time.time() # 이벤트 처리 시작
                    
                    # 딜레이 이벤트 처리
                    if event_type == 'delay':
                        # --- 디버깅 로그 추가 ---
                        print(f"--- Processing Delay Event ---")
                        print(f"Event Data: {event}") # 이벤트 객체 전체 출력
                        # --- 디버깅 로그 끝 ---

                        base_delay = event.get('delay', 0)
                        actual_delay = base_delay
                        if 'random_range' in event:
                             range_value = event.get('random_range', 0) # .get() 사용 권장
                             # range_value 타입 확인 및 변환 (안정성 강화)
                             try:
                                 range_value_float = float(range_value)
                             except (ValueError, TypeError):
                                 range_value_float = 0
                                 print(f"Warning: Invalid random_range '{range_value}', using 0.")

                             min_delay = max(0, base_delay - range_value_float)
                             max_delay = base_delay + range_value_float
                             actual_delay = random.uniform(min_delay, max_delay)
                             print(f"랜덤 딜레이: {base_delay:.3f}s ±{range_value_float:.3f}s → {actual_delay:.3f}s")
                        else:
                             print(f"일반 딜레이 값 (사용 전): {actual_delay:.3f}s")

                        # --- 디버깅 로그 추가 ---
                        print(f"Actual delay value for time.sleep(): {actual_delay:.3f}s (Type: {type(actual_delay)})")
                        # --- 디버깅 로그 끝 ---

                        sleep_start = time.time()
                        # *** 오직 딜레이 이벤트의 delay 값 만큼만 sleep ***
                        time.sleep(actual_delay)
                        delay_end_time = time.time()
                        print(f"[TimeLog] Finished delay event {i+1} at {delay_end_time:.3f} (slept {delay_end_time - sleep_start:.3f}s)")
                        continue
                    
                    # 딜레이가 아닌 이벤트는 바로 실행
                    if event_type == 'keyboard':
                        self._play_keyboard_event(event)
                    elif event_type == 'mouse':
                        # 기준 좌표 전달
                        self._play_mouse_event(event, self.base_x, self.base_y)
                
                    event_exec_end_time = time.time()
                    print(f"[TimeLog] Finished event {i+1} ({event_type}) execution at {event_exec_end_time:.3f} (took {event_exec_end_time - event_exec_start_time:.3f}s)")
                
                if not self.stop_requested and (repeat_count == 0 or current_repeat < repeat_count):
                    time.sleep(0.1) # 반복 사이 짧은 대기
            
            print("매크로 실행 완료/중단됨")
        except Exception as e:
            print(f"매크로 실행 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.playing = False # 종료 시 상태 확실히 변경
            logging.info(f"[Thread Check] 매크로 재생 스레드 종료. 활성 스레드 수: {threading.active_count()}") # 스레드 수 로그
            self.play_thread = None # 스레드 참조 제거
            log_memory_usage("Play Thread Ended") # 메모리 로그 추가
            gc.collect() # 가비지 컬렉션 강제 수행
            logging.info("[GC] 가비지 컬렉션 수행 완료.") # GC 로그 추가
    
    def _play_keyboard_event(self, event):
        """키보드 이벤트 실행"""
        try:
            key = event['key']
            event_type = event['event_type']
            
            if event_type == 'down':
                keyboard.press(key)
                print(f"키보드 누름: {key}")
            elif event_type == 'up':
                keyboard.release(key)
                print(f"키보드 떼기: {key}")
        except Exception as e:
            print(f"키보드 이벤트 실행 중 오류: {e}")
    
    def _play_mouse_event(self, event, base_x, base_y):
        """마우스 이벤트 실행 (3가지 좌표 모드 처리)"""
        try:
            event_type = event['event_type']
            target_pos_orig = list(event['position']) # 원본 상대/절대 좌표
            # is_relative = event.get('is_relative', False) # <<< is_relative 대신 coord_mode 사용
            coord_mode = event.get('coord_mode', 'absolute') # coord_mode 가져오기 (기본값 'absolute')
            
            # --- coord_mode 값에 따라 기준 좌표(base_target) 결정 --- 
            base_target_x, base_target_y = 0, 0
            
            if coord_mode == 'absolute':
                # 절대 좌표: 원본 좌표 그대로 사용
                base_target_x, base_target_y = target_pos_orig[0], target_pos_orig[1]
                print(f"마우스 절대 이동: Target({base_target_x}, {base_target_y})")
            elif coord_mode == 'gesture_relative':
                 # 제스처 상대 좌표: 제스처 시작 위치(base_x, base_y) 기준
                base_target_x = base_x + target_pos_orig[0]
                base_target_y = base_y + target_pos_orig[1]
                print(f"마우스 제스처 상대 이동: Base({base_x}, {base_y}) + Rel({target_pos_orig[0]}, {target_pos_orig[1]}) -> Target({base_target_x}, {base_target_y})")
            elif coord_mode == 'playback_relative':
                 # 마우스(재생) 상대 좌표: 현재 마우스 위치 기준
                try:
                    current_x, current_y = mouse.get_position()
                    base_target_x = current_x + target_pos_orig[0]
                    base_target_y = current_y + target_pos_orig[1]
                    print(f"마우스 재생 상대 이동: Current({current_x}, {current_y}) + Delta({target_pos_orig[0]}, {target_pos_orig[1]}) -> Target({base_target_x}, {base_target_y})")
                except Exception as e:
                    print(f"Error getting current mouse pos for playback_relative: {e}. Using gesture relative as fallback.")
                    # 오류 시 제스처 기준으로 fallback (안전 장치)
                    base_target_x = base_x + target_pos_orig[0]
                    base_target_y = base_y + target_pos_orig[1]
            else:
                 # 알 수 없는 모드 -> 절대 좌표로 처리 (안전 장치)
                print(f"Warning: Unknown coord_mode '{coord_mode}'. Treating as absolute.")
                base_target_x, base_target_y = target_pos_orig[0], target_pos_orig[1]

            # --- 기준 좌표 결정 끝 --- 
            
            # 랜덤 좌표 범위 처리 (결정된 기준 위치(base_target)에 적용)
            final_x, final_y = base_target_x, base_target_y
            if 'random_range' in event and event_type != 'scroll':
                range_px = event['random_range']
                # 정수로 변환 보장
                range_px_int = int(range_px) if isinstance(range_px, (int, float)) else 0
                if range_px_int > 0:
                    random_x = random.randint(base_target_x - range_px_int, base_target_x + range_px_int)
                    random_y = random.randint(base_target_y - range_px_int, base_target_y + range_px_int)
                    final_x, final_y = random_x, random_y # 최종 좌표 업데이트
                    print(f"랜덤 좌표 적용: BaseTarget({base_target_x}, {base_target_y}) ±{range_px_int}px → Final({final_x}, {final_y})")
            
            # 마우스 액션 수행 (계산된 final_x, final_y 사용)
            if event_type == 'move':
                mouse.move(final_x, final_y)
            elif event_type == 'down':
                button = event['button']
                mouse.move(final_x, final_y) # 이동 후 클릭
                mouse.press(button=button)
                print(f"마우스 {button} 누름: ({final_x}, {final_y})")
            elif event_type == 'up':
                button = event['button']
                mouse.move(final_x, final_y) # 이동 후 떼기
                mouse.release(button=button)
                print(f"마우스 {button} 떼기: ({final_x}, {final_y})")
            elif event_type == 'double':
                button = event['button']
                mouse.move(final_x, final_y) # 이동 후 더블클릭
                mouse.double_click(button=button)
                print(f"마우스 {button} 더블클릭: ({final_x}, {final_y})")
            elif event_type == 'scroll':
                delta = event['delta']
                # 스크롤은 특정 위치에서 발생해야 하는 경우가 많음
                mouse.move(final_x, final_y)
                mouse.wheel(delta=delta)
                print(f"마우스 스크롤: Delta {delta} at ({final_x}, {final_y})")
            elif event_type == 'wheel':
                delta = event.get('delta', 0)
                if delta != 0:
                    mouse.wheel(delta=delta)
                    print(f"마우스 휠 스크롤: Delta={delta}")
                else:
                    print("마우스 휠 이벤트 감지 (Delta=0), 스크롤하지 않음")
            
        except Exception as e:
            print(f"마우스 이벤트 실행 중 오류: {e}")
            import traceback
            traceback.print_exc()
    
    def is_playing(self):
        """매크로 실행 중인지 확인"""
        return self.playing 