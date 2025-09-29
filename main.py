import cv2
from cvcore.cvcore import CVCore  # Importing the CVCore class from the cvcore module

def main():
    cv_core = CVCore(win_name="CVTestingWindow")  # Create an instance of the CVCore class
    
    if not cv_core.InitializeVideoCapture():
        print("Failed to initialize video capture!")
        return
    
    # Print initial menu
    cv_core.PrintMenuAndStatus()
    
    while True: 
        # Process video frame
        if not cv_core.ProcessVideoFrame():
            print("Video processing ended")
            break
        
        # Check for keyboard input
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27:  # ESC key
            print("\nExiting...")
            break
        elif key == ord('1'):
            cv_core.SetDetectionMode("red")
            cv_core.PrintMenuAndStatus()
        elif key == ord('2'):
            cv_core.SetDetectionMode("blue")
            cv_core.PrintMenuAndStatus()
        elif key == ord('3'):
            cv_core.SetDetectionMode("green")
            cv_core.PrintMenuAndStatus()
        elif key == ord('4'):
            cv_core.SetDetectionMode("white")
            cv_core.PrintMenuAndStatus()
        elif key == ord('5'):
            cv_core.SetDetectionMode("orange")
            cv_core.PrintMenuAndStatus()
        elif key == ord('6'):
            cv_core.SetDetectionMode("bright")
            cv_core.PrintMenuAndStatus()
        elif key == ord('b') or key == ord('B'):
            cv_core.AddBrightColorSelection()
            cv_core.PrintMenuAndStatus()
        elif key == ord('a') or key == ord('A'):
            cv_core.SetDetectionMode("all")
            cv_core.PrintMenuAndStatus()
        elif key == ord('c') or key == ord('C'):
            cv_core.AddCustomColor()
            cv_core.PrintMenuAndStatus()
        elif key == ord('r') or key == ord('R'):
            cv_core.AddCustomColorFromRGB()
            cv_core.PrintMenuAndStatus()
        elif key == ord('s') or key == ord('S'):
            cv_core.ShowCustomColors()
            cv_core.PrintMenuAndStatus()

    #received shutdown signal.
    cv_core.Shutdown()

if __name__ == "__main__":
    main()
