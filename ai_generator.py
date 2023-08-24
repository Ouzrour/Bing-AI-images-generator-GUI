#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This TK Application is designed to automate the image
generation process, similar to Midjourney. It enables
the utilization of multiple accounts by leveraging
their respective cookies. These cookies provide direct
access to their services, eliminating the need for a web browser.

Done BY :  OUZROUR
Date : 20.8.23
"""

__author__ = "Ilyas Ouzrour"
__version__ = "1.0.0"
__email__ = "ilyas.ouzrour@gmail.com"
__status__ = "Production"

# ===========================================
#
# LIBRARIES
#
# ===========================================
# To Use .env variables
from dotenv import load_dotenv
# For selecting the directory (GUI)
from tkinter import filedialog
# Tkinter Library
import tkinter as tk
# To include the banner
from PIL import Image, ImageTk
# For context management
import contextlib
# For handling operating system functionalities
import os
# For generating random numbers
import random
# For system-specific parameters and functions
import sys
# For handling time-related functionalities
import time
# To create partial functions
from functools import partial
# For type hints
from typing import Dict, List, Union
# For multi-threading
import threading
# For regular expressions
import regex
# For making HTTP requests
import requests
# For parsing HTML content
from bs4 import BeautifulSoup

# ===========================================
#
# Constants
#
# ===========================================

# The Console Variable that stock the console Tk.Text Object
# To manipulate it with the ImageGen Class ( Out The Tkinter App )
# The Main Role is to show : Errors , Success ...
CONSOLE: tk.Text = None

# Load The .env
load_dotenv()

# The Link of bing
BING_URL = "https://www.bing.com"

# Generate random IP between range 13.104.0.0/14
FORWARDED_IP = (
    f"13.{random.randint(104, 107)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
)
HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "content-type": "application/x-www-form-urlencoded",
    "referrer": "https://www.bing.com/images/create/",
    "origin": "https://www.bing.com",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63",
    "x-forwarded-for": FORWARDED_IP,
}

# Error / Success messages
error_timeout = "Your request has timed out."
error_redirect = "Redirect failed"
error_blocked_prompt = (
    "Your prompt has been blocked by Bing. Try to change any bad words and try again."
)
error_being_reviewed_prompt = "Your prompt is being reviewed by Bing. Try to change any sensitive words and try again."
error_noresults = "Could not get results"
error_unsupported_lang = "\nthis language is currently not supported by bing"
error_bad_images = "Bad images"
error_no_images = "No images"
# Action messages
sending_message = "Sending request..."
wait_message = "Waiting for results..."
download_message = "\nDownloading images..."

# ===========================================
#
# Tools
#
# ===========================================


def resource_path(relative_path):
    """
    Change the relative path to an absolute
    Path ( to be used in Packaging with Pyinstaller )
    :param relative_path: The Relative Path
    """
    # Try to Get the base path ( for all OS )
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    # return the absolute path
    return os.path.join(base_path, relative_path)


def image_include(root, source: str, x: int, y: int):
    """
    Function for including the banner
    :param root: Tk Root Element
    :param source: The Source of image ( Absolute or Relative )
    :param x: position in axis of x
    :param y: position in axis of y
    :return: return a Tk label that include the image
    """
    # make the image readable with ImageTk module
    image = Image.open(source)
    imagetk = ImageTk.PhotoImage(image)
    # include it to a label
    label = tk.Label(root, image=imagetk, borderwidth=0)
    label.image = imagetk
    label.place(x=x, y=y)
    return label


def clear_placeholder( widget, variable):
    """
    clear automatically the placeholder of the output directory textbox
    if the default text in the placeholder ( variable ) is on it,
    and you want to tape something on it .
    :param widget: the Tk.textbox
    :param variable: The Default text in the placeholder
    :return:nothing
    """
    # if the content of the textbox is similar to the default text
    if widget.get() == variable:
        # delete the text
        widget.delete(0, tk.END)
        # change the color to black
        widget.config(fg="black")  # Change text color to black


def restore_placeholder(widget, variable):
    """
    Restore the value if nothing is typed
    :param widget: the Tk.textbox
    :param variable: The Default text in the placeholder
    :return:
    """
    # if nothing is written in the placeholder
    if not widget.get():
        # re-insert the default variable to it
        widget.insert(0, variable)
        # change the color to gray to make a difference between
        # the written value and the restored value
        widget.config(fg="gray")


def select_folder(text_box):
    """
    select the path of the folder using the Tkinter GUI
    :param text_box:the Tk.tk that you want to fill with the path
    :return:
    """
    # the function that use GUI to transform it to a string PATH
    selected_folder = filedialog.askdirectory()
    # if some folder is selected
    if selected_folder:
        # delete the textbox
        text_box.delete(0, tk.END)
        # insert the PATH value
        text_box.insert(0, selected_folder)
        # change the text to black
        text_box.config(fg="black")
# ===========================================
#
# The Full Design of The App
#
# ===========================================


class TkinterApp:
    """
    The Main Class of the app
    """
    def __init__(self, root):

        # root tk Element
        self.root = root

        # the title of the app
        self.root.title("AI Bing Image Generator - By. Ilyas Ouzrour")

        # the geometry of the app ( designed to fit this size , if you change it
        # you must change all the number in the rest of the code )
        self.root.geometry("660x660")
        self.root.minsize(660, 660)
        self.root.maxsize(660, 660)

        # The Background of the App ( Dark Mod )
        self.root.configure(background='black')

        # icon of the app
        icon_path = "assets/icon.ico"
        root.iconbitmap(icon_path)

        # ===========================================
        # The Header
        # ===========================================

        # Header
        image_include(root, resource_path("assets/bing-generator.png"), 0, 0)

        # ===========================================
        # The Left Side
        # ===========================================

        # list of cookies
        self.rows = []
        # the selected row ( the one whois radio button's is checked )
        self.selected_row = tk.IntVar()
        # The Creation of 12 cookies Row
        for i in range(12):
            self.rows.append(self.create_row(i))

        # ===========================================
        # The Right Frame
        # ===========================================

        # the Right frame :
        self.right_frame()

        # ===========================================
        # The Console Frame
        # ===========================================

        # Console part
        self.create_console()

        # ===========================================
        # The Footer
        # ===========================================

        # The footer
        self.footer()

    # ===========================================
    #
    # THE LEFT SIDE : Cookie's Part
    #
    # ===========================================

    def create_row(self, row_number):
        """
        A function that creates a row (containing the cookie address)
        :param row_number: The row number for identification
        :return: A tuple containing the created elements of the row: (radio_button,
         text_box, button, label)
        """
        # The Frame of the Row
        row_frame = tk.Frame(self.root,background="gray")
        row_frame.place(x=0, y=100+30*row_number, width=360, height=30)

        # The Radio button of the Row
        radio_button = tk.Radiobutton(row_frame, variable=self.selected_row, value=row_number, background="gray",
                                      selectcolor="DodgerBlue2", indicatoron=0)
        radio_button.place(x=2, y=5, width=20, height=20)

        # The Textbox of the Row
        text_box = tk.Entry(row_frame,background="gray89")
        text_box.place(x=25, y=5, width=250, height=20)
        # if we have cookies saved in .env
        if os.getenv(f"COOKIE{row_number+1}") is not None :
            text_box.insert(0,os.getenv(f"COOKIE{row_number+1}"))
        # The "Check" button
        button = tk.Button(row_frame, text="Check", command=lambda row=row_number: self.cookie_check(row),background="white")
        button.place(x=277, y=5, width=53, height=20)

        # The Rest of the coin ( after the check )
        label = tk.Label(row_frame, text="-",background="gray")
        label.place(x=330, y=5, width=30, height=20)
        label.config(fg="white", font=("Helvetica", 10, "bold"))

        # Return all the values of the row
        return (radio_button, text_box, button, label)

    def cookie_check(self, row_number):
        """
        Check if the Cookie in the row work or Not
        :param row_number: The Number of the row to be verified
        :return: Nothing , if Error : an Error msg
        """
        # extract the values ( text , label ) from the selected row
        _, selected_text, _, selected_label = self.rows[row_number]
        try:
            # Use the function get_token_balance to extract the value of the
            # remain token linked to the account ( cookie )
            token_balance = get_token_balance(selected_text.get())

            # if the function return the coin value
            if token_balance is not None:
                # change the label to the coin value
                selected_label.config(text=token_balance)
                # a message in the console to alert the user that all things work fine
                self.console.insert("end", ' \n =========================== \n')
                self.console.insert("end", " || SUCCES : CONNECTED ! \n")
                self.console.insert("end", " || Token Balance : "+token_balance)
                self.console.insert("end", ' \n =========================== \n ')
                # configuration of the design of the label
                selected_text.config(bg="green4",fg="white", font=("Helvetica", 10, "bold"))
                selected_label.config(fg="chartreuse2")

            else:
                # a message in the console to alert the user that we have an error
                self.console.insert("end", ' \n =========================== \n')
                self.console.insert("end", " || FAIL ! \n","red")
                self.console.insert("end", ' || ERROR :  Unable to fetch token balance or wrong cookie syntax or empty. ',"red")
                self.console.insert("end", ' \n =========================== \n ')
                # configuration of the design of the label
                selected_text.config(bg="red4",fg="white", font=("Helvetica", 10, "bold"))
                selected_label.config(text="ERR",fg="pink")
            # Scroll to the end to keep the latest content visible
            self.console.see("end")

        except Exception as e:
            # a message in the console to alert the user that we have an error
            self.console.insert("end", ' \n =========================== \n ')
            self.console.insert("end", f"An error occurred: {e}" , "red")
            CONSOLE.see("end")


    # ===========================================
    #
    # THE RIGHT SIDE : Request's Part + Parameters & Run Part
    #
    # ===========================================

    def right_frame(self):
        """
        Tk Design for the right Part of the App
        :return: Nothing
        """
        # ===========================================
        # Request Part
        # ===========================================

        # Request Label

        label = tk.Label(self.root, text="The Request", background="DodgerBlue2")
        label.place(x=362, y=100, width=298, height=30)
        label.config(fg="white", font=("Helvetica", 11, "bold"))

        # Request Text Label

        self.request_box = tk.Text(self.root, background="white")
        self.request_box.place(x=361, y=130, width=299, height=170)
        self.request_box.config(fg="black", font=("Helvetica", 10, "bold"))
        # Bind the <Return> key event to the launched function
        self.request_box.bind("<Return>", lambda event: self.run_the_process())

        # ===========================================
        # Output Part
        # ===========================================

        # OUTDIR Label

        label = tk.Label(self.root, text="Output Directory :",background="black")
        label.place(x=362, y=302, width=298, height=19)
        label.config(fg="white", font=("Helvetica", 10, "bold"),anchor="w")

        # OUTDIR Textbox

        self.out_dir = tk.Entry(self.root, background="gray92")
        self.out_dir.place(x=362, y=322, width=197, height=25)
        default_text = "/output"
        # if the element OUTDIR exist in .env
        if os.getenv("OUTDIR") != "" :
            default_text = os.getenv("OUTDIR")
        self.out_dir.insert(0, default_text)  # Insert default text
        self.out_dir.bind("<FocusIn>", lambda event: clear_placeholder(self.out_dir, default_text))
        self.out_dir.bind("<FocusOut>", lambda event: restore_placeholder(self.out_dir, default_text))

        # OUTDIR "choose" button

        icon_button = tk.Button(self.root, text="Choose", command=lambda tb=self.out_dir: select_folder(tb),
                                background="yellow" , fg="black")
        icon_button.place(x=560, y=321,width=100, height=27)

        # ===========================================
        # Download Part
        # ===========================================

        # max download Label

        download = tk.Label(self.root, text="Max. Images to be downloaded :", background="DodgerBlue4")
        download.place(x=360, y=350, width=300, height=35)
        download.config(fg="white", font=("Helvetica", 11, "bold"))

        # max download Functional part

        self.selected_number = tk.IntVar()
        # default value
        self.selected_number.set(4)

        # decrease button
        decrement_button = tk.Button(self.root, text="-", command=self.decrement_number)
        decrement_button.place(x=360, y=385, width=60, height=25)

        # the number of downloads
        number_label = tk.Label(self.root, textvariable=self.selected_number,background="DodgerBlue3")
        number_label.place(x=420, y=385, width=180, height=25)
        number_label.config(fg="white", font=("Helvetica", 11, "bold"))

        # increase button
        increment_button = tk.Button(self.root, text="+", command=self.increment_number)
        increment_button.place(x=600, y=385, width=60, height=25)

        # ===========================================
        # Run Button Part
        # ===========================================

        # RUN BUTTON :

        increment_button = tk.Button(self.root, text="RUN THE SCRIPT", command=self.run_the_process)
        increment_button.place(x=361, y=412, width=299, height=48)
        increment_button.config(fg="white", font=("Helvetica", 12, "bold"),background="DodgerBlue2")

    def decrement_number(self):
        """
        Decrement the number of max download
        :return: Nothing
        """
        if self.selected_number.get() > 1:
            # decrement the value by 1

            self.selected_number.set(self.selected_number.get() - 1)

    def increment_number(self):
        """
        Increment the number of max download
        :return: Nothing
        """
        if self.selected_number.get() < 4:
            # increment the value by 1
            self.selected_number.set(self.selected_number.get() + 1)

    def run_the_process(self):
        """
        The Process that Use All The Class of the ImageGen
        - The Must Important Function in this code -
        :return: str "break" to not break the line when we click "enter" button in the request part
        """
        # Load auth cookie ( parameter in ImageGen functions )
        cookie_json = None
        # First , we must be sure that the selected row have a valid cookie
        # to work with it
        self.cookie_check(self.selected_row.get())
        # extract the values (text,label) from the selected row
        _, selected_text, _, selected_label = self.rows[self.selected_row.get()]
        # if the cookie work fine ( the coin value is well displayed ) : all things work fine
        if not ( selected_label.cget("text") == "ERR" or selected_label.cget("text") == "-" ):
            # initialize the value of the output directory
            output_directory: str = ""
            # if the person don't change anything ( don't choose a specific folder )
            if self.out_dir.get() == "/output":
                # work with the folder /output in same path of the code (.py)
                output_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
            # if the element exist in .env
            elif os.getenv("OUTDIR") != "" :
                output_directory = os.getenv("OUTDIR")
            else :
                # work with the chosen folder
                output_directory = self.out_dir.get()

            # Create image generator
            def start_request_loop():
                image_generator = ImageGen(
                    selected_text.get(),
                    None,
                    False,
                    all_cookies=cookie_json,
                )
                image_generator.save_images(
                    image_generator.get_images(self.request_box.get("1.0", "end-1c")),
                    output_dir=resource_path(output_directory),
                    download_count=int(self.selected_number.get()),
                )

            # I use the threading because of the use of time.sleep() function
            # in ImageGen.save_images() who freeze the tkinter loop ( a common error )

            request_thread = threading.Thread(target=start_request_loop)
            request_thread.start()
        return "break"
    # ===========================================
    #
    # The Console
    #
    # ===========================================
    def create_console(self):
        """
        the function that create the console
        :return:
        """
        # the console as Tk.text
        self.console = tk.Text(self.root,background="black")
        # set a default tag ( to change the color of the errors )
        self.console.tag_configure("red", foreground="red")
        # initialize the global CONSOLE variable to be used in ImageGen Class
        global CONSOLE
        CONSOLE = self.console
        # set the font of the console
        self.console.config(fg="green2", font=("Helvetica", 8, "bold"))
        # set the position of the console
        self.console.place(x=0, y=461, width=660, height=179)

        # The Steps ( showed when the console initialize )

        self.console.insert("end", " By: Ilyas Ouzrour | Github : github.com/Ouzrour "
                                   "-- & -- acheong08 | Github : github.com/acheong08\n")
        self.console.insert("end", "--------------------------------------- \n")
        self.console.insert("end", " The Steps : \n")
        self.console.insert("end", "--------------------------------------- \n")
        self.console.insert("end", " 1. fill the cookie(s) tab (The Method is in Readme.md)  \n")
        self.console.insert("end", ' 2. Check if the cookie work by clicking the "check" button\n')
        self.console.insert("end", ' 3. select a cookie with a score big than 0 \n')
        self.console.insert("end", ' 4. write your request in the request part \n')
        self.console.insert("end", ' 5. select the Output directory ( by default : /output ) \n')
        self.console.insert("end", ' 6. Choose the maximum number of images to download (1-4) \n')
        self.console.insert("end", ' 7. click the "Run Button" \n')

    # ===========================================
    #
    # Footer
    #
    # ===========================================
    def footer(self):
        footer = tk.Label(self.root, text="Made By : Ilyas Ouzrour ( ilyas.ouzrour@gmail.com )", background="blue4")
        footer.place(x=0, y=640, width=660, height=20)
        footer.config(fg="white", font=("Helvetica", 10, "bold"))

    # ===========================================
    #
    # Run Function
    #
    # ===========================================

    def run(self):
        """
        Initialize the radio buttons and run the app
        :return:
        """
        for i in range(8):
            radio_button, _, _, _ = self.rows[i]
            radio_button.config(variable=self.selected_row)
        self.root.mainloop()

# This function isn't used, but I don't want to delete it
# because I may use it in the further Updates .
# Used to save the debug rapport in a file

def debug(debug_file, text_var):
    """helper function for debug"""
    with open(f"{debug_file}", "a", encoding="utf-8") as f:
        f.write(str(text_var))
        f.write("\n")
class ImageGen:
    """
    Image generation by Microsoft Bing
    Parameters:
        auth_cookie: str
        auth_cookie_SRCHHPGUSR: str
    Optional Parameters:
        debug_file: str
        quiet: bool
        all_cookies: List[Dict]
    """

    def __init__(
            self,
            auth_cookie: str,
            auth_cookie_SRCHHPGUSR: str,
            debug_file: Union[str, None] = None,
            quiet: bool = False,
            all_cookies: List[Dict] = None,
    ) -> None:
        self.session: requests.Session = requests.Session()
        self.session.headers = HEADERS
        self.session.cookies.set("_U", auth_cookie)
        self.session.cookies.set("SRCHHPGUSR", auth_cookie_SRCHHPGUSR)
        if all_cookies:
            for cookie in all_cookies:
                self.session.cookies.set(cookie["name"], cookie["value"])
        self.quiet = quiet
        self.debug_file = debug_file
        if self.debug_file:
            self.debug = partial(debug, self.debug_file)

    def get_images(self, prompt: str) -> list:
        """
        Fetches image links from Bing
        Parameters:
            prompt: str
        """
        if not self.quiet:
            CONSOLE.insert("end", f"\n{sending_message} ")
            CONSOLE.see("end")
        if self.debug_file:
            self.debug(sending_message)
        url_encoded_prompt = requests.utils.quote(prompt)
        payload = f"q={url_encoded_prompt}&qs=ds"
        # https://www.bing.com/images/create?q=<PROMPT>&rt=3&FORM=GENCRE
        url = f"{BING_URL}/images/create?q={url_encoded_prompt}&rt=4&FORM=GENCRE"
        response = self.session.post(
            url,
            allow_redirects=False,
            data=payload,
            timeout=200,
        )
        # check for content waring message
        if "this prompt is being reviewed" in response.text.lower():
            if self.debug_file:
                self.debug(f"ERROR: {error_being_reviewed_prompt}")
            CONSOLE.insert("end", f"\n ERROR: {error_being_reviewed_prompt} \n","red")
            CONSOLE.see("end")

        if "this prompt has been blocked" in response.text.lower():
            if self.debug_file:
                self.debug(f"ERROR: {error_blocked_prompt}")
            CONSOLE.insert("end", f"\n ERROR: {error_blocked_prompt} \n","red")
            CONSOLE.see("end")

        if (
                "we're working hard to offer image creator in more languages"
                in response.text.lower()
        ):
            if self.debug_file:
                self.debug(f"ERROR: {error_unsupported_lang}")
            CONSOLE.insert("end", f"\n ERROR: {error_unsupported_lang} \n","red")
            CONSOLE.see("end")

        if response.status_code != 302:
            # if rt4 fails, try rt3
            url = f"{BING_URL}/images/create?q={url_encoded_prompt}&rt=3&FORM=GENCRE"
            response = self.session.post(url, allow_redirects=False, timeout=200)
            if response.status_code != 302:
                if self.debug_file:
                    self.debug(f"ERROR: {error_redirect}")
                CONSOLE.insert("end", f"\n ERROR: {response.text} \n","red")
                CONSOLE.see("end")
                CONSOLE.insert("end", f"\n {error_redirect} \n","red")
                CONSOLE.see("end")

        # Get redirect URL
        redirect_url = response.headers["Location"].replace("&nfy=1", "")
        request_id = redirect_url.split("id=")[-1]
        self.session.get(f"{BING_URL}{redirect_url}")
        # https://www.bing.com/images/create/async/results/{ID}?q={PROMPT}
        polling_url = f"{BING_URL}/images/create/async/results/{request_id}?q={url_encoded_prompt}"
        # Poll for results
        if self.debug_file:
            self.debug("Polling and waiting for result")
        if not self.quiet:
            CONSOLE.insert("end", "\n Waiting for results...")
            CONSOLE.see("end")

        start_wait = time.time()
        while True:
            if int(time.time() - start_wait) > 200:
                if self.debug_file:
                    self.debug(f"ERROR: {error_timeout}")
                CONSOLE.insert("end", f"{error_timeout}","red")
                CONSOLE.see("end")
            if not self.quiet:
                CONSOLE.insert("end", ".")
            response = self.session.get(polling_url)
            if response.status_code != 200:
                if self.debug_file:
                    self.debug(f"ERROR: {error_noresults}")
                CONSOLE.insert("end", f"\n {error_noresults} \n","red")
                CONSOLE.see("end")

            if not response.text or response.text.find("errorMessage") != -1:
                time.sleep(1)
                continue
            else:
                break
        # Use regex to search for src=""
        image_links = regex.findall(r'src="([^"]+)"', response.text)
        soup = BeautifulSoup(response.text, 'html.parser')
        global div_element  # Declare the variable as global within the function
        div_element = response.text
        # Remove size limit
        normal_image_links = [link.split("?w=")[0] for link in image_links]
        # Remove duplicates
        normal_image_links = list(set(normal_image_links))

        # Bad images
        bad_images = [
            "https://r.bing.com/rp/in-2zU3AJUdkgFe7ZKv19yPBHVs.png",
            "https://r.bing.com/rp/TX9QuO3WzcCJz1uaaSwQAz39Kb0.jpg",
        ]
        for img in normal_image_links:
            if img in bad_images:
                CONSOLE.insert("end", f"\n Bad images \n","red")
                CONSOLE.see("end")
        # No images
        if not normal_image_links:
            CONSOLE.insert("end", f"\n {error_no_images} \n","red")
            CONSOLE.see("end")
        return normal_image_links

    def save_images(
            self,
            links: list,
            output_dir: str,
            file_name: str = None,
            download_count: int = None,
    ) -> None:
        """
        Saves images to output directory
        Parameters:
            links: list[str]
            output_dir: str
            file_name: str
            download_count: int
        """
        if self.debug_file:
            self.debug(download_message)
        if not self.quiet:
            CONSOLE.insert("end", f" {download_message} \n")
            CONSOLE.see("end")

        with contextlib.suppress(FileExistsError):
            os.mkdir(output_dir)
        try:
            fn = f"{file_name}_" if file_name else ""
            jpeg_index = 0

            if download_count:
                links = links[:download_count]

            for link in links:
                while os.path.exists(
                        os.path.join(output_dir, f"{fn}{jpeg_index}.jpeg")
                ):
                    jpeg_index += 1
                response = self.session.get(link)
                if response.status_code != 200:
                    CONSOLE.insert("end", "\n Could not download image \n","red")
                    CONSOLE.see("end")
                # save response to file
                with open(
                        os.path.join(output_dir, f"{fn}{jpeg_index}.jpeg"), "wb"
                ) as output_file:
                    output_file.write(response.content)
                jpeg_index += 1
            CONSOLE.insert("end", "\n ---------------------------------------------------- \n")
            CONSOLE.insert("end", "\n -----------> DONE : ENJOY ! By.Ouzrour \n")
            CONSOLE.insert("end", "\n ---------------------------------------------------- \n")
            CONSOLE.see("end")

        except requests.exceptions.MissingSchema as url_exception:
            CONSOLE.insert("end", "\n Inappropriate contents found in the generated images. Please try again or try another prompt. \n","red")
            CONSOLE.see("end")


def get_token_balance(auth_cookie):
    """
    A function that check if the cookie work
    :param auth_cookie: the cookie to test it
    :return:
    """
    headers = {
        "User-Agent": HEADERS["user-agent"],
    }
    cookies = {
        "_U": auth_cookie,
    }
    response = requests.get("https://www.bing.com/images/create?", headers=headers, cookies=cookies)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        token_bal_element = soup.find('div', {'id': 'token_bal'})

        if token_bal_element:
            token_bal_text = token_bal_element.get_text(strip=True)
            return token_bal_text
    return None


if __name__ == "__main__":
    root = tk.Tk()
    app = TkinterApp(root)
    app.run()
