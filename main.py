import cv2
from cvcore.cvcore import CVCore  # Importing the CVCore class from the cvcore module

def main():
    cv_core = CVCore(win_name="done")  # Create an instance of the CVCore class
    cv_core.AddImage("rec\\enough_for_today.png")
    cv_core.AddImage("rec\\toaster_bath.png")  # Adding another image for demonstration

    cv_core.Render(cv_core.GetCurrentImage())

    while True:
        if cv_core.CheckWindowClosed() or cv2.waitKey(1) == 27:  # Check if window is closed or ESC key is pressed
            break
        elif cv2.waitKey(1) == ord('1'):
            cv_core.ChangeCurrentImage(0)
            cv_core.Render(cv_core.GetCurrentImage())
        elif cv2.waitKey(1) == ord('2'):
            cv_core.ChangeCurrentImage(1)
            cv_core.Render(cv_core.GetCurrentImage())

    #received shutdown signal.
    cv_core.Shutdown()

if __name__ == "__main__":
    main()
