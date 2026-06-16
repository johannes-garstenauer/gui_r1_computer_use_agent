import pyautogui
import requests
import base64
import re
import time
import sys
from io import BytesIO

# --- HIGH-DPI SCALING FIX (Windows Only) ---
if sys.platform == 'win32':
    import ctypes
    try:
        # Modern Windows 10/11 Per-Monitor DPI Awareness
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        print("🔧 Windows Modern High-DPI Awareness Enabled.")
    except Exception:
        # Fallback for older systems
        ctypes.windll.user32.SetProcessDPIAware()

# PyAutoGUI Safety: Moving mouse to any corner of the screen aborts the script
pyautogui.FAILSAFE = True 

# --- The GUI-R1 System Prompt ---
SYSTEM_PROMPT = """You are GUI-R1, a reasoning GUI Agent Assistant. In this UI screenshot < image >, I
want you to continue executing the command task, with the action history being history.
Please provide the action to perform (enumerate from [complete, close/delete,
press home, click, press back, type, select, scroll, enter]), the point where the
cursor is moved to (integer) if a click is performed, and any input text required to complete
the action.
Output the thinking process in <think> </think> tags, and the final answer
in <answer> </answer> tags as follows: <think> ... </think>
<answer>{'action': '...', 'point': [x, y], 'input_text': '...'}</answer>.
"""

def get_screenshot_as_base64():
    """Captures ONLY the primary screen and compresses it."""
    screen_width, screen_height = pyautogui.size()
    image = pyautogui.screenshot(region=(0, 0, screen_width, screen_height))
    buffered = BytesIO()
    image.save(buffered, format="JPEG", quality=85)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def ask_gui_r1(prompt_text, history_log):
    """Sends the system prompt, user prompt, image, and history to the cluster."""
    img_b64 = get_screenshot_as_base64()
    
    # 1. Format the history log
    if not history_log:
        history_text = "None (this is the first step)."
    else:
        history_text = "\n".join([f"Step {i+1}: {act}" for i, act in enumerate(history_log)])
        
    # 2. Inject history safely into the System Prompt
    current_system_prompt = SYSTEM_PROMPT.replace("being history.", f"being:\n{history_text}\n")
    
    print("\n🧠 Sending data to NHR@FAU cluster... (Waiting for inference)")
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "/home/woody/iwso/iwso234h/gui_r1_weights/GUI-R1-3B", # Ensure this path is correct!
        "messages": [
            {"role": "system", "content": current_system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Instruction: {prompt_text}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                ]
            }
        ],
        "temperature": 0.1,
        "max_tokens": 512
    }
    
    try:
        response = requests.post("http://localhost:8000/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"❌ Connection Error! {e}")
        return None

def wow_factor_targeting(x, y):
    """Visually highlights the target for the audience before acting."""
    pyautogui.moveTo(x, y, duration=0.6, tween=pyautogui.easeInOutQuad)
    pyautogui.moveRel(10, 0, duration=0.05)
    pyautogui.moveRel(-10, 10, duration=0.05)
    pyautogui.moveRel(-10, -10, duration=0.05)
    pyautogui.moveRel(10, -10, duration=0.05)
    pyautogui.moveTo(x, y, duration=0.05)
    time.sleep(0.2)

def execute_action(model_output):
    """Parses and executes the full GUI-R1 action space, returning a history string."""
    
    answer_match = re.search(r"<answer>(.*?)</answer>", model_output, re.IGNORECASE | re.DOTALL)
    if not answer_match:
         print("⚠️ Model failed to generate <answer> tags.")
         return None
         
    answer_block = answer_match.group(1)

    action_match = re.search(r"['\"]action['\"]\s*:\s*['\"](.*?)['\"]", answer_block)
    point_match = re.search(r"['\"]point['\"]\s*:\s*\[(\d+),\s*(\d+)\]", answer_block)
    text_match = re.search(r"['\"](?:input_text|text)['\"]\s*:\s*['\"](.*?)['\"]", answer_block)

    if not action_match:
        print("⚠️ Could not determine the action from model output.")
        return None

    action = action_match.group(1).lower()
    action_summary = ""
    
    print("\n" + "="*40)
    print(f"🤖 AGENT DECISION: [{action.upper()}]")
    
    # -----------------------------------------
    # NEW: Non-Spatial / System Actions
    # -----------------------------------------
    if action == 'complete':
        print("🎉 Agent reports the task is COMPLETE!")
        print("="*40 + "\n")
        return "COMPLETE"
        
    elif action == 'press home':
        pyautogui.press('win')
        action_summary = "Pressed the Home (Windows) button."
        
    elif action == 'press back':
        pyautogui.hotkey('alt', 'left')
        action_summary = "Pressed the Browser Back button."
        
    elif action == 'close/delete':
        pyautogui.hotkey('ctrl', 'w')
        action_summary = "Pressed Close/Delete (Ctrl+W)."
        
    elif action == 'enter':
        pyautogui.press('enter')
        action_summary = "Pressed the Enter key."
        
    # -----------------------------------------
    # Spatial Mouse Actions
    # -----------------------------------------
    elif action in ['click', 'double_click', 'right_click', 'hover', 'select']:
        if not point_match:
            print("⚠️ Spatial action requires coordinates!")
            return None
            
        target_x = int(float(point_match.group(1)))
        target_y = int(float(point_match.group(2)))
        print(f"📍 Target Coordinates: ({target_x}, {target_y})")
        
        wow_factor_targeting(target_x, target_y)

        if action == 'click' or action == 'select':
            pyautogui.click()
            action_summary = f"Clicked at [{target_x}, {target_y}]."
        elif action == 'double_click':
            pyautogui.doubleClick()
            action_summary = f"Double-clicked at [{target_x}, {target_y}]."
        elif action == 'right_click':
            pyautogui.rightClick()
            action_summary = f"Right-clicked at [{target_x}, {target_y}]."
        elif action == 'hover':
            action_summary = f"Hovered over [{target_x}, {target_y}]."
            
    # -----------------------------------------
    # Typing & Scrolling
    # -----------------------------------------
    elif action == 'type':
        type_string = text_match.group(1) if text_match else ""
        print(f"⌨️  Typing text: '{type_string}'")
        
        if point_match:
            target_x = int(float(point_match.group(1)))
            target_y = int(float(point_match.group(2)))
            wow_factor_targeting(target_x, target_y)
            pyautogui.click()
            
        pyautogui.write(type_string, interval=0.05)
        pyautogui.press('enter')
        action_summary = f"Typed '{type_string}' and pressed Enter."

    elif action == 'scroll':
        print("↕️  Scrolling interface...")
        pyautogui.scroll(-500) 
        action_summary = "Scrolled down the page."
        
    else:
        print(f"⚠️ Unknown action type: {action}")
        return None
        
    print("="*40 + "\n")
    print("⏳ Waiting for UI animations to settle...")
    time.sleep(1.5)
    
    return action_summary

# --- The Continuous Demo Loop ---
if __name__ == "__main__":
    print("🚀 Starting GUI-R1 Local Demo (Continuous Mode)")
    print("⚠️  SAFETY: Slam your mouse into any corner of the screen to Emergency Abort.\n")
    
    # NEW: Initialize the agent's memory
    action_history = []
    
    while True:
        try:
            # If history is empty, prompt the user for a new task.
            # If history has items, we are in the middle of a multi-step task!
            if not action_history:
                user_prompt = input("\n🎯 Enter NEW task (or type 'exit' to quit): ")
                if user_prompt.lower() in ['exit', 'quit']:
                    print("Ending demo...")
                    break
                if user_prompt.strip() == "":
                    continue
            else:
                print(f"\n🔄 Continuing task: '{user_prompt}'")
            
            print("⏳ Switching to target window... (Taking screenshot in 2 seconds)")
            time.sleep(2)
            
            response_text = ask_gui_r1(user_prompt, action_history)
            
            if response_text:
                # Execute the action and get the summary for our history log
                result_summary = execute_action(response_text)
                
                if result_summary == "COMPLETE":
                    # Task is done! Clear memory so we can ask a new question.
                    action_history = []
                elif result_summary:
                    # Add to history, keeping only the last 5 actions to save context space
                    action_history.append(result_summary)
                    action_history = action_history[-5:]
                else:
                    # If parsing failed, clear history to prevent getting permanently stuck
                    action_history = []
                
        except pyautogui.FailSafeException:
            print("\n🚨 EMERGENCY ABORT TRIGGERED: Mouse moved to screen corner.")
            break
        except KeyboardInterrupt:
            print("\nDemo terminated by user.")
            break