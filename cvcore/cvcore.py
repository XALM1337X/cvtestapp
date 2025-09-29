import cv2
import numpy as np

class CVCore:
    def __init__(self, win_name="default"):
        
        self.WindowName = win_name
        self.VideoCapture = None
        self.IsVideoMode = False
        self.CurrentFrame = None

        # Detection mode properties
        self.DetectionMode = "all"  # "all", "red", "blue", "green", etc.
        self.ColorRanges = {
            "red": [(0, 50, 50), (10, 255, 255)],      # Red color range in HSV
            "blue": [(100, 50, 50), (130, 255, 255)],  # Blue color range in HSV
            "green": [(40, 50, 50), (80, 255, 255)],    # Green color range in HSV
            "white": [(0, 0, 200), (180, 30, 255)],     # White: low saturation, high brightness
            "orange": [(5, 50, 50), (25, 255, 255)]     # Orange color range in HSV
        }
        
        # Custom color properties
        self.CustomColors = {}  # Store custom colors by name
        self.CurrentCustomColor = None  # Currently selected custom color
        self.BrightColorMode = None  # Current bright color mode (e.g., "bright_green")
        
        cv2.namedWindow(winname=win_name)

    def InitializeVideoCapture(self, source=0):
        """
        Initialize video capture
        source: 0 for webcam, or path to video file
        Returns: True if successful, False if failed
        """
        self.VideoCapture = cv2.VideoCapture(source)

        # Step 2: Check if it opened successfully
        if self.VideoCapture.isOpened():
            self.IsVideoMode = True
            print(f"Video capture initialized successfully from source: {source}")
            return True
        else:
            print(f"Failed to open video source: {source}")
            return False

    def ProcessVideoFrame(self):
        """
        Get next frame and process it with simple object detection
        Returns: True if frame was processed, False if video ended
        """
        frame = self.GetNextFrame()

        if frame is not None:
            # Use simple object detection
            detected_frame = self.DetectObjects(frame)
            self.RenderFrame(detected_frame)
            return True
        return False


    def DetectObjects(self, frame):
        """
        Simple object detection - detects objects based on current detection mode
        """
        if self.DetectionMode == "all":
            return self.DetectAllObjects(frame)
        elif self.DetectionMode == "bright":
            if self.BrightColorMode:
                return self.DetectBrightColorObjects(frame, self.BrightColorMode)
            else:
                return self.DetectBrightObjects(frame)
        else:
            return self.DetectColorObjects(frame, self.DetectionMode)

    def DetectAllObjects(self, frame):
        """
        Detect all objects using edge detection
        """
        result_frame = frame.copy()
        
        # Convert to grayscale and find contours
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)
        edges = cv2.Canny(blurred, 30, 100)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by area and draw outlines
        object_count = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Only draw outlines around objects larger than 500 pixels
            if area > 500:
                object_count += 1
                # Draw green outline around the object
                cv2.drawContours(result_frame, [contour], -1, (0, 255, 0), 3)
                
                # Draw centroid as a small circle
                centroid = self.CalculateCentroid(contour)
                cv2.circle(result_frame, centroid, 5, (0, 255, 0), -1)
                
                # Get and display the average RGB color
                avg_color = self.GetAverageColor(frame, contour)
                color_text = f"RGB{avg_color}"
                
                # Draw color text above the centroid
                text_position = (centroid[0] - 40, centroid[1] - 30)
                cv2.putText(result_frame, color_text, text_position, 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                cv2.putText(result_frame, color_text, text_position, 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        # Update console with simple status
        print(f"\rDetected {object_count} objects (all)", end="", flush=True)
        
        return result_frame

    def DetectBrightColorObjects(self, frame, color_name):
        """
        Detect bright versions of a specific color (perfect for LED lights)
        """
        result_frame = frame.copy()
        
        # Convert BGR to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Get the color range for the specified color
        if color_name in self.ColorRanges:
            lower_color, upper_color = self.ColorRanges[color_name]
        elif color_name in self.CustomColors:
            lower_color, upper_color = self.CustomColors[color_name]
        else:
            print(f"\rInvalid color: {color_name}", end="", flush=True)
            return result_frame
        
        # Modify the color range to only include bright versions
        # Keep the hue and saturation ranges, but increase minimum brightness
        lower_bright_color = np.array([lower_color[0], lower_color[1], 180])  # High brightness
        upper_bright_color = np.array([upper_color[0], upper_color[1], 255])  # Max brightness
        
        # Create mask for bright versions of the specific color
        mask = cv2.inRange(hsv, lower_bright_color, upper_bright_color)
        
        # Apply morphological operations to clean up the mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Draw outlines around detected bright color objects
        object_count = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Only draw outlines around objects larger than 200 pixels (LEDs can be smaller)
            if area > 200:
                object_count += 1
                # Draw outline around the object
                cv2.drawContours(result_frame, [contour], -1, (0, 255, 0), 3)
                
                # Draw centroid as a small circle
                centroid = self.CalculateCentroid(contour)
                cv2.circle(result_frame, centroid, 5, (0, 255, 0), -1)
                
                # Get and display the average RGB color
                avg_color = self.GetAverageColor(frame, contour)
                color_text = f"RGB{avg_color}"
                
                # Draw color text above the centroid
                text_position = (centroid[0] - 40, centroid[1] - 30)
                cv2.putText(result_frame, color_text, text_position, 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                cv2.putText(result_frame, color_text, text_position, 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        # Update console with bright color objects status
        print(f"\rDetected {object_count} bright {color_name} objects (LED lights)", end="", flush=True)
        
        return result_frame

    def DetectBrightObjects(self, frame):
        """
        Detect objects based on high brightness (light intensity)
        """
        result_frame = frame.copy()
        
        # Convert BGR to HSV for brightness analysis
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Create mask for high brightness objects
        # High brightness = well-lit objects, low brightness = dark objects
        lower_brightness = np.array([0, 0, 180])    # Any hue, any saturation, high brightness
        upper_brightness = np.array([179, 255, 255]) # Any hue, any saturation, max brightness
        
        mask = cv2.inRange(hsv, lower_brightness, upper_brightness)
        
        # Apply some morphological operations to clean up the mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Draw outlines around detected bright objects
        object_count = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Only draw outlines around objects larger than 300 pixels
            if area > 300:
                object_count += 1
                # Draw outline around the object
                cv2.drawContours(result_frame, [contour], -1, (0, 255, 0), 3)
                
                # Draw centroid as a small circle
                centroid = self.CalculateCentroid(contour)
                cv2.circle(result_frame, centroid, 5, (0, 255, 0), -1)
                
                # Get and display the average RGB color
                avg_color = self.GetAverageColor(frame, contour)
                color_text = f"RGB{avg_color}"
                
                # Draw color text above the centroid
                text_position = (centroid[0] - 40, centroid[1] - 30)
                cv2.putText(result_frame, color_text, text_position, 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                cv2.putText(result_frame, color_text, text_position, 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        # Update console with bright objects status
        print(f"\rDetected {object_count} bright objects (high brightness)", end="", flush=True)
        
        return result_frame

    def DetectColorObjects(self, frame, color_name):
        """
        Detect objects of a specific color
        """
        result_frame = frame.copy()
        
        # Convert BGR to HSV for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Get color range for the specified color
        if color_name in self.ColorRanges:
            lower_color, upper_color = self.ColorRanges[color_name]
        elif color_name in self.CustomColors:
            lower_color, upper_color = self.CustomColors[color_name]
        else:
            print(f"\rUnknown color: {color_name}", end="", flush=True)
            return result_frame
            
        # Create mask for the color
        mask = cv2.inRange(hsv, lower_color, upper_color)
        
        # Apply some morphological operations to clean up the mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Draw outlines around detected color objects
        object_count = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Only draw outlines around objects larger than 300 pixels (lower threshold for color detection)
            if area > 300:
                object_count += 1
                # Draw outline around the object
                cv2.drawContours(result_frame, [contour], -1, (0, 255, 0), 3)
                
                # Draw centroid as a small circle
                centroid = self.CalculateCentroid(contour)
                cv2.circle(result_frame, centroid, 5, (0, 255, 0), -1)
                
                # Get and display the average RGB color
                avg_color = self.GetAverageColor(frame, contour)
                color_text = f"RGB{avg_color}"
                
                # Draw color text above the centroid
                text_position = (centroid[0] - 40, centroid[1] - 30)
                cv2.putText(result_frame, color_text, text_position, 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                cv2.putText(result_frame, color_text, text_position, 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        # Update console with color-specific status
        print(f"\rDetected {object_count} {color_name} objects", end="", flush=True)
        
        return result_frame

    def RenderFrame(self, frame=None):
        """
        Display a frame in the window
        frame: frame to display, if None uses CurrentFrame
        """
        if frame is None:
            frame = self.CurrentFrame
        
        if frame is not None:
            cv2.imshow(self.WindowName, frame)
    

    def SetBrightColorMode(self, color_name):
        """
        Set the bright color mode for LED detection
        """
        if color_name in self.ColorRanges or color_name in self.CustomColors:
            self.BrightColorMode = color_name
        else:
            self.BrightColorMode = None

    def AddBrightColorSelection(self):
        """
        Non-blocking interactive function to select bright color for LED detection.
        """
        print("\n=== Bright Color Selection ===")
        print("Select a color for bright/LED detection (1-6) or ESC to cancel (5s timeout):")
        print("1: Bright Red LEDs")
        print("2: Bright Blue LEDs")
        print("3: Bright Green LEDs")
        print("4: Bright White LEDs")
        print("5: Bright Orange LEDs")
        print("6: Any Bright Color (reset)")

        key = -1
        start_time = cv2.getTickCount()
        while (cv2.getTickCount() - start_time) / cv2.getTickFrequency() < 5: # 5 second timeout
            key = cv2.waitKey(1) & 0xFF
            if key != 255: # A key was pressed
                break
        
        if key == 27: # ESC
            print("\nCancelled.")
            return
        
        selected_color = None
        if key == ord('1'):
            selected_color = "red"
        elif key == ord('2'):
            selected_color = "blue"
        elif key == ord('3'):
            selected_color = "green"
        elif key == ord('4'):
            selected_color = "white"
        elif key == ord('5'):
            selected_color = "orange"
        elif key == ord('6'):
            selected_color = None  # Reset to any bright color
        else:
            print("\nInvalid selection or timeout.")
            return

        self.SetBrightColorMode(selected_color)
        if selected_color:
            print(f"\nSet bright color mode to: {selected_color} LEDs")
        else:
            print(f"\nReset to detect any bright objects")

    def AddCustomColorHSV(self, name, hsv_range):
        """
        Add a custom color for detection using a direct HSV range.
        name: string name for the color
        hsv_range: ((lower_h, lower_s, lower_v), (upper_h, upper_s, upper_v)) tuple
        """
        self.CustomColors[name] = hsv_range

    def AddCustomColor(self):
        """
        Non-blocking HSV range selector for custom color detection
        """
        print("\n=== HSV Range Selector ===")
        print("Select a predefined HSV range:")
        print("1. Red range (good for most red objects)")
        print("2. Blue range (good for most blue objects)")
        print("3. Green range (good for most green objects)")
        print("4. Yellow range (good for yellow objects)")
        print("5. Purple range (good for purple objects)")
        print("6. Orange range (good for orange objects)")
        
        # Predefined HSV ranges that work well in different lighting
        predefined_ranges = {
            "1": ("red_advanced", ((0, 50, 50), (20, 255, 255))),
            "2": ("blue_advanced", ((100, 50, 50), (130, 255, 255))),
            "3": ("green_advanced", ((40, 50, 50), (80, 255, 255))),
            "4": ("yellow_advanced", ((20, 50, 50), (40, 255, 255))),
            "5": ("purple_advanced", ((130, 50, 50), (160, 255, 255))),
            "6": ("orange_advanced", ((5, 50, 50), (25, 255, 255)))
        }
        
        print("\nPress 1-6 to select, or ESC to cancel:")
        
        # Non-blocking input using cv2.waitKey
        choice = None
        timeout = 0
        while timeout < 50:  # 5 second timeout
            key = cv2.waitKey(100) & 0xFF
            if key == 27:  # ESC
                print("Cancelled.")
                return
            elif key == ord('1'):
                choice = "1"
                break
            elif key == ord('2'):
                choice = "2"
                break
            elif key == ord('3'):
                choice = "3"
                break
            elif key == ord('4'):
                choice = "4"
                break
            elif key == ord('5'):
                choice = "5"
                break
            elif key == ord('6'):
                choice = "6"
                break
            timeout += 1
        
        if choice is None:
            print("Timeout - cancelled.")
            return
        
        if choice in predefined_ranges:
            name, hsv_range = predefined_ranges[choice]
            self.AddCustomColorHSV(name, hsv_range)
            print(f"\nAdded '{name}' with HSV range: {hsv_range}")
            print("Press the corresponding number key to use this color detection.")

    def ShowCustomColors(self):
        """
        Show all custom colors
        """
        print("\n=== Custom Colors ===")
        if self.CustomColors:
            for name, hsv_range in self.CustomColors.items():
                print(f"'{name}': HSV{hsv_range}")
        else:
            print("No custom colors added yet.")
        print("Press a number key (6-9) to use a custom color, or add more with 'C'")

    def AddCustomColorFromRGB(self):
        """
        Non-blocking RGB to HSV converter with predefined tolerances
        """
        print("\n=== RGB to HSV Converter ===")
        print("Select a color and tolerance level:")
        print("1. Pure Red (RGB: 255,0,0) - High tolerance")
        print("2. Pure Blue (RGB: 0,0,255) - High tolerance")
        print("3. Pure Green (RGB: 0,255,0) - High tolerance")
        print("4. Pure Yellow (RGB: 255,255,0) - High tolerance")
        print("5. Pure Purple (RGB: 128,0,128) - High tolerance")
        print("6. Pure Orange (RGB: 255,165,0) - High tolerance")
        
        # Predefined RGB colors with good HSV tolerances
        rgb_colors = {
            "1": ("red_rgb", (255, 0, 0), ((0, 50, 50), (20, 255, 255))),
            "2": ("blue_rgb", (0, 0, 255), ((100, 50, 50), (130, 255, 255))),
            "3": ("green_rgb", (0, 255, 0), ((40, 50, 50), (80, 255, 255))),
            "4": ("yellow_rgb", (255, 255, 0), ((20, 50, 50), (40, 255, 255))),
            "5": ("purple_rgb", (128, 0, 128), ((130, 50, 50), (160, 255, 255))),
            "6": ("orange_rgb", (255, 165, 0), ((5, 50, 50), (25, 255, 255)))
        }
        
        print("\nPress 1-6 to select, or ESC to cancel:")
        
        # Non-blocking input using cv2.waitKey
        choice = None
        timeout = 0
        while timeout < 50:  # 5 second timeout
            key = cv2.waitKey(100) & 0xFF
            if key == 27:  # ESC
                print("Cancelled.")
                return
            elif key == ord('1'):
                choice = "1"
                break
            elif key == ord('2'):
                choice = "2"
                break
            elif key == ord('3'):
                choice = "3"
                break
            elif key == ord('4'):
                choice = "4"
                break
            elif key == ord('5'):
                choice = "5"
                break
            elif key == ord('6'):
                choice = "6"
                break
            timeout += 1
        
        if choice is None:
            print("Timeout - cancelled.")
            return
        
        if choice in rgb_colors:
            name, rgb_color, hsv_range = rgb_colors[choice]
            self.AddCustomColorHSV(name, hsv_range)
            print(f"\nAdded '{name}' from RGB{rgb_color} with HSV range: {hsv_range}")
            print("Press the corresponding number key to use this color detection.")

    def PrintMenuAndStatus(self):
        """
        Print the menu and current detection status
        """
        print("\n" + "="*50)
        print("OBJECT DETECTION CONTROLS")
        print("="*50)
        print("ESC - Exit")
        print("1 - Detect red objects")
        print("2 - Detect blue objects") 
        print("3 - Detect green objects")
        print("4 - Detect white objects")
        print("5 - Detect orange objects")
        print("6 - Detect bright objects (high brightness)")
        print("B - Select bright color for LED detection")
        print("A - Detect all objects")
        print("C - Add custom color (HSV range editor)")
        print("R - Add custom color (RGB converter)")
        print("S - Show custom colors")
        print("-"*50)
        print(f"CURRENT MODE: {self.DetectionMode.upper()}")
        if self.DetectionMode == "bright" and self.BrightColorMode:
            print(f"BRIGHT COLOR: {self.BrightColorMode.upper()} LEDs")
        elif self.DetectionMode == "bright":
            print("BRIGHT COLOR: Any bright objects")
        
        # Show custom colors if any exist
        if self.CustomColors:
            print("CUSTOM COLORS AVAILABLE:")
            for name in self.CustomColors.keys():
                print(f"  - {name}")
            print("Press 'S' to see HSV ranges")
        
        print("="*50)

    def SetDetectionMode(self, mode):
        """
        Set the detection mode
        """
        if mode in ["all", "red", "blue", "green", "white", "orange", "bright"] or mode in self.CustomColors:
            self.DetectionMode = mode
        else:
            print(f"\nInvalid detection mode: {mode}")

    def RGBToHSVRange(self, rgb_color, tolerance=30):
        """
        Convert RGB color to HSV range for detection
        rgb_color: (R, G, B) tuple (0-255)
        tolerance: how much variation to allow (0-255)
        Returns: (lower_hsv, upper_hsv) tuple
        """
        # Convert single RGB color to HSV
        import numpy as np
        rgb_array = np.uint8([[rgb_color]])
        hsv_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2HSV)
        h, s, v = hsv_array[0][0]
        
        # Create range with tolerance
        lower_h = max(0, h - tolerance)
        upper_h = min(179, h + tolerance)  # HSV hue max is 179
        lower_s = max(0, s - tolerance)
        upper_s = min(255, s + tolerance)
        lower_v = max(0, v - tolerance)
        upper_v = min(255, v + tolerance)
        
        return ((lower_h, lower_s, lower_v), (upper_h, upper_s, upper_v))

    def AddCustomColor(self, name, rgb_color, tolerance=30):
        """
        Add a custom color for detection
        name: string name for the color
        rgb_color: (R, G, B) tuple (0-255)
        tolerance: detection tolerance (0-255)
        """
        hsv_range = self.RGBToHSVRange(rgb_color, tolerance)
        self.CustomColors[name] = hsv_range

    def GetNextFrame(self):
        """
        Get the next frame from video capture
        Returns: frame array if successful, None if failed or end of video
        """
        if self.VideoCapture is None or not self.VideoCapture.isOpened():
            return None
        
        ret, frame = self.VideoCapture.read()
        
        if ret:
            self.CurrentFrame = frame
            return frame
        else:
            return None

    def CalculateCentroid(self, contour):
        """
        Calculate the center point (centroid) of a contour
        Returns: (x, y) tuple representing the centroid
        """
        # Calculate the moments of the contour
        moments = cv2.moments(contour)
        
        # Calculate centroid coordinates
        if moments["m00"] != 0:  # Avoid division by zero
            cx = int(moments["m10"] / moments["m00"])
            cy = int(moments["m01"] / moments["m00"])
            return (cx, cy)
        else:
            # If moments["m00"] is zero, use bounding rectangle center
            x, y, w, h = cv2.boundingRect(contour)
            return (x + w//2, y + h//2)

    def GetAverageColor(self, frame, contour):
        """
        Get the average RGB color of pixels within a contour
        Returns: (R, G, B) tuple
        """
        # Create a mask for the contour
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [contour], 255)
        
        # Get the mean color of pixels within the mask
        mean_color = cv2.mean(frame, mask=mask)
        
        # Return RGB values (OpenCV returns BGR, so reverse it)
        return (int(mean_color[2]), int(mean_color[1]), int(mean_color[0]))




    def Shutdown(self):
        cv2.destroyAllWindows()