Nirmal Chaturvedi, [05-03-2024 09:08]
import cv2
from PIL import Image, ImageTk
import face_recognition
import os
import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import datetime
import pandas as pd
from openpyxl import load_workbook

class CameraApp:
    def init(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        self.video_source = 0  # Use default camera (change if you have multiple cameras)
        self.frame_width = 640  # Width of the processed frame
        self.frame_height = 480  # Height of the processed frame

        self.vid = cv2.VideoCapture(self.video_source)

        self.canvas = tk.Canvas(window, width=self.frame_width, height=self.frame_height)
        self.canvas.pack()

        self.btn_open_camera = tk.Button(window, text="Open Camera", width=20, command=self.open_camera)
        self.btn_open_camera.pack(pady=10)

        self.btn_close = tk.Button(window, text="Close", width=20, command=self.close_camera)
        self.btn_close.pack(pady=10)

        self.is_camera_open = False
        self.unknown_name = None
        self.adhar_id = None
        self.pan_id = None

        # Load known face images and encodings
        self.known_faces_directory = "C:/Users/Nirmal chaturvedi/Desktop/known_faces"
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_known_faces()

        # Create directory to store unknown faces
        self.unknown_faces_directory = "C:/Users/Nirmal chaturvedi/Desktop/now"
        self.create_directory(self.unknown_faces_directory)

        # Create Excel file to store Aadhar number, PAN card number, and name
        self.excel_file = "C:/Users/Nirmal chaturvedi/Desktop/hi.xlsx"
        self.create_excel()

        # Cooldown period for face detection (in seconds)
        self.cooldown_duration = 5
        self.last_detection_time = datetime.now()

        self.update()

        # Add entry field for searching
        self.search_entry = tk.Entry(window)
        self.search_entry.pack(pady=10)

        # Add search button
        self.btn_search = tk.Button(window, text="Search", width=20, command=self.search_person)
        self.btn_search.pack(pady=5)

        # Add scrollbar and text widget for search result
        self.scrollbar = tk.Scrollbar(window)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.search_result_text = tk.Text(window, height=10, width=50, yscrollcommand=self.scrollbar.set)
        self.search_result_text.pack(pady=5)
        self.scrollbar.config(command=self.search_result_text.yview)

    def open_camera(self):
        if not self.is_camera_open:
            self.is_camera_open = True
            self.btn_open_camera.config(text="Close Camera")
            self.vid = cv2.VideoCapture(self.video_source)

    def load_known_faces(self):
        if not os.path.exists(self.known_faces_directory):
            print(f"Directory '{self.known_faces_directory}' does not exist.")
            return

        print("Loading known faces...")

        for filename in os.listdir(self.known_faces_directory):
            name, ext = os.path.splitext(filename)
            if ext.lower() in (".jpg", ".jpeg", ".png"):
                print(f"Loading face: {name}")
                image_path = os.path.join(self.known_faces_directory, filename)
                image = face_recognition.load_image_file(image_path)
                encoding = face_recognition.face_encodings(image)[0]
                self.known_face_encodings.append(encoding)
                self.known_face_names.append(name)

    def create_directory(self, directory):
        if not os.path.exists(directory):
            print(f"Creating directory: {directory}")
            os.makedirs(directory)

    def create_excel(self):
        if not os.path.exists(self.excel_file):
            print(f"Creating Excel file: {self.excel_file}")
            df = pd.DataFrame(columns=["Name", "Aadhar ID", "PAN ID"])
            df.to_excel(self.excel_file, index=False)

Nirmal Chaturvedi, [05-03-2024 09:08]
def update(self):
        if self.is_camera_open:
            ret, frame = self.vid.read()

            if ret:
                # Resize the frame
                frame = cv2.resize(frame, (self.frame_width, self.frame_height))

                # Convert the frame to RGB for face_recognition library
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Find all face locations in the frame
                face_locations = face_recognition.face_locations(rgb_frame)
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

                # Get current time
                current_time = datetime.now()

                # Match faces with stored faces
                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    if (current_time - self.last_detection_time).total_seconds() >= self.cooldown_duration:
                        matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                        name = "Unknown"
                        color = (0, 0, 255)  # Default color: red (for unknown faces)
                        if True in matches:
                            index = matches.index(True)
                            name = self.known_face_names[index]
                            color = (255, 0, 0)  # Blue color for known faces

                        # Draw rectangle around the face and label it
                        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                        if name == "Unknown":
                            if self.unknown_name is None:
                                self.unknown_name = self.ask_name()  # Ask for the name of the unknown face
                                self.adhar_id = self.ask_adhar_id()  # Ask for Aadhar ID
                                self.pan_id = self.ask_pan_id()  # Ask for PAN ID

                                # Check if Aadhar and PAN already exist
                                if not self.check_duplicate(self.adhar_id, self.pan_id):
                                    # Save details to Excel
                                    self.save_to_excel(self.unknown_name, self.adhar_id, self.pan_id)

                            name = self.unknown_name  # Assign the entered name to the face

                            # Debugging output
                            print("Saving unknown face")
                            print("Name:", name)
                            print("Coordinates:", (top, right, bottom, left))

                            # Save the frame containing the detected face
                            self.save_face_frame(rgb_frame, self.adhar_id)

                            # Update last detection time
                            self.last_detection_time = current_time

                        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

                # Convert the frame back to RGB for displaying in tkinter
                self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

            else:
                self.close_camera()  # Stop update when video ends

        self.window.after(10, self.update)

    def ask_name(self):
        name = simpledialog.askstring("Input", "Enter the name of the unknown face:")
        return name

    def ask_adhar_id(self):
        adhar_id = simpledialog.askstring("Input", "Enter Aadhar ID:")
        return adhar_id

    def ask_pan_id(self):
        pan_id = simpledialog.askstring("Input", "Enter PAN ID:")
        return pan_id

    def close_camera(self):
        if self.is_camera_open:
            self.is_camera_open = False
            self.btn_open_camera.config(text="Open Camera")
            if self.vid.isOpened():
                self.vid.release()

    def save_face_frame(self, frame, adhar_id):
        # Convert frame to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

Nirmal Chaturvedi, [05-03-2024 09:08]
# Get current time for unique filename
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        # Save the frame as an image file in the known_faces directory
        filename = os.path.join(self.known_faces_directory, f"{adhar_id}.jpg")
        success = cv2.imwrite(filename, gray_frame)
        if success:
            print(f"Saved face frame: {filename}")
        else:
            print(f"Failed to save face frame: {filename}")

    def save_to_excel(self, name, adhar_id, pan_id):
        data = {"Name": [name], "Aadhar ID": [adhar_id], "PAN ID": [pan_id]}
        df = pd.DataFrame(data)

        if os.path.exists(self.excel_file):
            print(f"Appending to Excel file: {self.excel_file}")
            # Load the existing Excel file
            wb = load_workbook(self.excel_file)
            ws = wb.active

            # Append data to the Excel file
            for row in df.iterrows():
                values = list(row[1])
                ws.append(values)

            # Save the modified Excel file
            wb.save(self.excel_file)
            messagebox.showinfo("Success", "Record inserted successfully!")
        else:
            print(f"Creating new Excel file: {self.excel_file}")
            df.to_excel(self.excel_file, index=False)
            messagebox.showinfo("Success", "Record inserted successfully!")

    def check_duplicate(self, adhar_id, pan_id):
        try:
            df = pd.read_excel(self.excel_file)
            if adhar_id in df['Aadhar ID'].values or pan_id in df['PAN ID'].values:
                messagebox.showinfo("Duplicate Record", "Duplicate Aadhar ID or PAN ID found.")
                return True
            else:
                return False
        except KeyError:
            return False

    def search_person(self):
        search_query = self.search_entry.get()
        if search_query:
            result = self.search_in_excel(search_query)
            self.display_search_result(result)
        else:
            messagebox.showinfo("Error", "Please enter Aadhar number or PAN number for search.")

    def search_in_excel(self, query):
        try:
            df = pd.read_excel(self.excel_file)
            result = df[(df['Aadhar ID'] == query) | (df['PAN ID'] == query)]
            return result
        except KeyError:
            print("Error: Aadhar ID or PAN ID column not found in Excel file.")
            return None
        except Exception as e:
            print("Error during search:", e)
            return None

    def display_search_result(self, result):
        self.search_result_text.delete(1.0, tk.END)  # Clear previous search result
        if result is not None and not result.empty:
            result_str = "Search Result:\n" + result.to_string(index=False)
            self.search_result_text.insert(tk.END, result_str)
        else:
            self.search_result_text.insert(tk.END, "No matching record found.")

# Create a window and pass it to the CameraApp class
root = tk.Tk()
app = CameraApp(root, "Camera App")
root.mainloop()
