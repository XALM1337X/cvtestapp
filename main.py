import cv2
from cvcore.cvcore import CVCore  # Importing the CVCore class from the cvcore module

def main():
    cv_core = CVCore(win_name="done")  # Create an instance of the CVCore class
    cv_core.AddImage("enough_for_today.png")
    cv_core.AddImage("toaster_bath.png")  # Adding another image for demonstration

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

if __name__ == "__main__":
    main()
    cv2.destroyAllWindows()


"""
pic = Image.open("enough_for_today.png")
pic_arr = np.asarray(pic)
pic_red = pic_arr.copy()
pic_blue= pic_arr.copy()
pic_green= pic_arr.copy()

pic_red[:,:,1]=0
pic_red[:,:,2]=0

pic_blue[:,:,0]=0
pic_blue[:,:,1]=0

pic_green[:,:,0]=0
pic_green[:,:,2]=0



# Display the red, green, and blue "gray scale" images
fig, axs = plt.subplots(2, 3, figsize=(15, 5))
axs[0,0].imshow(pic_red)
axs[0,0].set_title('Red Channel')
axs[0,0].axis('off')

axs[0,1].imshow(pic_blue)
axs[0,1].set_title('Green Channel')
axs[0,1].axis('off')

axs[0,2].imshow(pic_green)
axs[0,2].set_title('Blue Channel')
axs[0,2].axis('off')

axs[1,0].imshow(pic_red[:,:,0], cmap='gray')
axs[1,0].set_title('Red gray Channel')
axs[1,0].axis('off')

axs[1,1].imshow(pic_blue[:,:,2], cmap='gray')
axs[1,1].set_title('Blue gray Channel')
axs[1,1].axis('off')

axs[1,2].imshow(pic_green[:,:,1], cmap='gray')
axs[1,2].set_title('Green gray Channel')
axs[1,2].axis('off')

plt.show()
"""