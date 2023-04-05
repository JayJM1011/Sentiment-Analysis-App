import tkinter as tk
import pandas as pd
import pickle
from PIL import Image, ImageTk

class MainWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        #UI
        self.title("Login Window")
        self.geometry("270x135")
        ico= tk.PhotoImage(file= "ico.png")
        self.iconphoto(False, ico)
        #Widgets
        self.username_label = tk.Label(self, text="Username:")
        self.username_label.grid(row=0, column=0, padx=5, pady=5)

        self.username_entry = tk.Entry(self)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        self.password_label = tk.Label(self, text="Password:")
        self.password_label.grid(row=1, column=0, padx=5, pady=5)

        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.login_button = tk.Button(self, text="Login", command=self.check_login)
        self.login_button.grid(row=2, column=1, padx=5, pady=5)

        self.login_label = tk.Label(self, text="")
        self.login_label.grid(row=3, column=0, columnspan=2, padx=10, pady=0)

    def check_login(self):
        #Code-------------------------------
        upass= pd.read_csv("user_pass.csv")
        man= pd.read_csv("man_det.csv")
        uman, users, passs= [], [], []
        for index, row in upass.iterrows():
            users.append(row["EMPLOYEE_ID"])
            passs.append(row["PASSWORDS"])
        for index, row in man.iterrows():
            uman.append(row["EMPLOYEE_ID"])
        uman.sort()
        
        username= int(self.username_entry.get())
        password = str(self.password_entry.get())
        #Code End---------------------------
        if  username in users and password == (passs[users.index(username)]):
            self.login_label.config(text="Login successful!")
            # self.master.sleep(2)
            # root.destroy()
            # sleep(2)
            
            if username == 100:
                BossWindow(self.master)
            elif username in uman:
                with open('sentiment_analysis_model.pkl', 'rb') as f:
                    self.sent= pickle.load(f)
                ManagerWindow(self.master, username, self.sent)
            else:
                with open('sentiment_analysis_model.pkl', 'rb') as f:
                    self.sent= pickle.load(f)
                EmployeeWindow(self.master, username, self.sent)

        else:
            self.login_label.config(text= "Re-enter !")

class EmployeeWindow(tk.Toplevel):
    def __init__(self, master, username, sent):
        super().__init__(master)
        self.title("Employee Window")
        self.geometry("600x150")
        ico= tk.PhotoImage(file= "ico.png")
        self.iconphoto(False, ico)
        
        self.review_e = tk.Entry(self)
        self.review_e.place(x=20, y=20, width= 550, height= 50)

        self.submit_review_e = tk.Button(self, text="Submit", command=self.rev_e)
        self.submit_review_e.place(x=260, y=100, width=80, height=40)

        self.u= username
        self.s= sent
        
    def rev_e(self):
        # get the new value from the text box
        r_e = str(self.review_e.get())
        
        # Load the CSV file into a pandas DataFrame
        emp_df = pd.read_csv("emp_man.csv")
        
        # update the specified cell in the DataFrame

        emp_df.loc[emp_df["EMPLOYEE_ID"] == self.u, "REVIEWS"] = r_e
        array= self.s(r_e)[0]
        if array["label"] == "POS":
            if array["score"] > 0.98:
                r_e_s= "EXH"
            else:
                r_e_s= "HAP"
        elif array["label"] == "NEG":
            if array["score"] > 0.98:
                r_e_s= "EXS"
            else:
                r_e_s= "SAD"
        else:
            r_e_s= "NEU"
        emp_df.loc[emp_df["EMPLOYEE_ID"] == self.u, "SENTIMENTS"] = r_e_s
        
        # write the updated DataFrame back to the CSV file
        emp_df.to_csv("emp_man.csv", index=False)

class ManagerWindow(tk.Toplevel):
    def __init__(self, master, username, sent):
        super().__init__(master)
        self.title("Manager Window")
        self.geometry('450x300')
        ico= tk.PhotoImage(file= "ico.png")
        self.iconphoto(False, ico)
        
        #getting the sentiments of the manager's employees
        self.man_df= pd.read_csv("emp_man.csv")
        sents= self.man_df.loc[self.man_df["MANAGER_ID"].values == username]["SENTIMENTS"].values
        Sents= []

        for i in sents:
            if i == "EXH":
                Sents.append(10)
            if i == "HAP":
                Sents.append(8)
            if i == "NEU":
                Sents.append(5)
            if i == "0":
                Sents.append(5)
            if i == "SAD":
                Sents.append(2)
            if i == "EXS":
                Sents.append(0)

        sent_to_man= int(sum(Sents) / len(Sents))

        #displaying the sentiment
        if sent_to_man >= 8:
            image= Image.open("V_Happy.png").resize((200, 200))
        elif sent_to_man >= 6:
            image= Image.open("Happy.png").resize((200, 200))
        elif sent_to_man >= 4:
            image= Image.open("Moderate_Average.png").resize((200, 200))
        elif sent_to_man >= 2:
            image= Image.open("Sad.png").resize((200, 200))
        else:
            image= Image.open("V_Sad.png").resize((200, 200))
        self.man_sent_image= ImageTk.PhotoImage(image)
        self.img_label= tk.Label(self, image= self.man_sent_image)
        self.img_label.pack()

        self.review_m = tk.Entry(self)
        self.review_m.place(x=20, y=220, width=280, height=40)
        self.submit_review_m = tk.Button(self, text='Submit', command= self.rev_m)
        self.submit_review_m.place(x=320, y=220, width=80, height=40)


        self.u= username
        self.s= sent
        
    def rev_m(self):
        #get review
        r_m = str(self.review_m.get())
        
        #update csv
        self.man_df.loc[self.man_df["EMPLOYEE_ID"] == self.u, "REVIEWS"] = r_m

        #sentiment analysis
        array= self.s(r_m)[0]
        if array["label"] == "POS":
            if array["score"] > 0.98:
                r_e_s= "EXH"
            else:
                r_e_s= "HAP"
        elif array["label"] == "NEG":
            if array["score"] > 0.98:
                r_e_s= "EXS"
            else:
                r_e_s= "SAD"
        else:
            r_e_s= "NEU"
        self.man_df.loc[self.man_df["EMPLOYEE_ID"] == self.u, "SENTIMENTS"] = r_e_s
        
        #replace csv
        self.man_df.to_csv("emp_man.csv", index=False)

class BossWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Boss Window")
        self.geometry("450x300")
        ico= tk.PhotoImage(file= "ico.png")
        self.iconphoto(False, ico)
        
        boss_df= pd.read_csv("emp_man.csv")

        #images and sentiments of managers
        #sent_image(self, "101")
        S= boss_df.loc[boss_df["EMPLOYEE_ID"].values == 101]["SENTIMENTS"].values[0]
        if S == "EXH":
            self.image_sent_1= ImageTk.PhotoImage(Image.open("V_Happy.png").resize((90, 90)))
        elif S == "HAP":
            self.image_sent_1= ImageTk.PhotoImage(Image.open("Happy.png").resize((90, 90)))
        elif S == "SAD":
            self.image_sent_1= ImageTk.PhotoImage(Image.open("Sad.png").resize((90, 90)))
        elif S == "EXS":
            self.image_sent_1=  ImageTk.PhotoImage(Image.open("V_Sad.png").resize((90, 90)))
        else:
            self.image_sent_1=  ImageTk.PhotoImage(Image.open("Moderate_Average.png").resize((90, 90)))

        self.man1_img = tk.Label(self, image= self.image_sent_1)
        self.man1_img.place(x= 30, y= 20)
        self.man1_id = tk.Label(self, text= "101")
        self.man1_id.place(x= 60, y= 120)

        # sent_image(self, "102")
        S= boss_df.loc[boss_df["EMPLOYEE_ID"].values == 102]["SENTIMENTS"].values[0]
        if S == "EXH":
            self.image_sent_2= ImageTk.PhotoImage(Image.open("V_Happy.png").resize((90, 90)))
        elif S == "HAP":
            self.image_sent_2= ImageTk.PhotoImage(Image.open("Happy.png").resize((90, 90)))
        elif S == "SAD":
            self.image_sent_2= ImageTk.PhotoImage(Image.open("Sad.png").resize((90, 90)))
        elif S == "EXS":
            self.image_sent_2=  ImageTk.PhotoImage(Image.open("V_Sad.png").resize((90, 90)))
        else:
            self.image_sent_2=  ImageTk.PhotoImage(Image.open("Moderate_Average.png").resize((90, 90)))

        self.man2_img = tk.Label(self, image= self.image_sent_2)
        self.man2_img.place(x= 135, y= 20)
        self.man2_id = tk.Label(self, text= "102")
        self.man2_id.place(x= 165, y= 120)

        # sent_image(self, "120")
        S= boss_df.loc[boss_df["EMPLOYEE_ID"].values == 120]["SENTIMENTS"].values[0]
        if S == "EXH":
            self.image_sent_3= ImageTk.PhotoImage(Image.open("V_Happy.png").resize((90, 90)))
        elif S == "HAP":
            self.image_sent_3= ImageTk.PhotoImage(Image.open("Happy.png").resize((90, 90)))
        elif S == "SAD":
            self.image_sent_3= ImageTk.PhotoImage(Image.open("Sad.png").resize((90, 90)))
        elif S == "EXS":
            self.image_sent_3=  ImageTk.PhotoImage(Image.open("V_Sad.png").resize((90, 90)))
        else:
            self.image_sent_3=  ImageTk.PhotoImage(Image.open("Moderate_Average.png").resize((90, 90)))

        self.man3_img = tk.Label(self, image= self.image_sent_3)
        self.man3_img.place(x= 240, y= 20)
        self.man3_id = tk.Label(self, text= "120")
        self.man3_id.place(x= 270, y= 120)

        # sent_image(self, "121")
        S= boss_df.loc[boss_df["EMPLOYEE_ID"].values == 121]["SENTIMENTS"].values[0]
        if S == "EXH":
            self.image_sent_4= ImageTk.PhotoImage(Image.open("V_Happy.png").resize((90, 90)))
        elif S == "HAP":
            self.image_sent_4= ImageTk.PhotoImage(Image.open("Happy.png").resize((90, 90)))
        elif S == "SAD":
            self.image_sent_4= ImageTk.PhotoImage(Image.open("Sad.png").resize((90, 90)))
        elif S == "EXS":
            self.image_sent_4=  ImageTk.PhotoImage(Image.open("V_Sad.png").resize((90, 90)))
        else:
            self.image_sent_4=  ImageTk.PhotoImage(Image.open("Moderate_Average.png").resize((90, 90)))

        self.man4_img = tk.Label(self, image= self.image_sent_4)
        self.man4_img.place(x= 345, y= 20)
        self.man4_id = tk.Label(self, text= "121")
        self.man4_id.place(x= 375, y= 120)

        # sent_image(self, "122")
        S= boss_df.loc[boss_df["EMPLOYEE_ID"].values == 122]["SENTIMENTS"].values[0]
        if S == "EXH":
            self.image_sent_5= ImageTk.PhotoImage(Image.open("V_Happy.png").resize((90, 90)))
        elif S == "HAP":
            self.image_sent_5= ImageTk.PhotoImage(Image.open("Happy.png").resize((90, 90)))
        elif S == "SAD":
            self.image_sent_5= ImageTk.PhotoImage(Image.open("Sad.png").resize((90, 90)))
        elif S == "EXS":
            self.image_sent_5=  ImageTk.PhotoImage(Image.open("V_Sad.png").resize((90, 90)))
        else:
            self.image_sent_5=  ImageTk.PhotoImage(Image.open("Moderate_Average.png").resize((90, 90)))

        self.man5_img = tk.Label(self, image= self.image_sent_5)
        self.man5_img.place(x= 30, y= 160)
        self.man5_id = tk.Label(self, text= "122")
        self.man5_id.place(x= 60, y= 260)

        # sent_image(self, "123")
        S= boss_df.loc[boss_df["EMPLOYEE_ID"].values == 123]["SENTIMENTS"].values[0]
        if S == "EXH":
            self.image_sent_6= ImageTk.PhotoImage(Image.open("V_Happy.png").resize((90, 90)))
        elif S == "HAP":
            self.image_sent_6= ImageTk.PhotoImage(Image.open("Happy.png").resize((90, 90)))
        elif S == "SAD":
            self.image_sent_6= ImageTk.PhotoImage(Image.open("Sad.png").resize((90, 90)))
        elif S == "EXS":
            self.image_sent_6=  ImageTk.PhotoImage(Image.open("V_Sad.png").resize((90, 90)))
        else:
            self.image_sent_6=  ImageTk.PhotoImage(Image.open("Moderate_Average.png").resize((90, 90)))

        self.man6_img = tk.Label(self, image= self.image_sent_6)
        self.man6_img.place(x= 135, y= 160)
        self.man6_id = tk.Label(self, text= "123")
        self.man6_id.place(x= 165, y= 260)

        # sent_image(self, "124")
        S= boss_df.loc[boss_df["EMPLOYEE_ID"].values == 124]["SENTIMENTS"].values[0]
        if S == "EXH":
            self.image_sent_7= ImageTk.PhotoImage(Image.open("V_Happy.png").resize((90, 90)))
        elif S == "HAP":
            self.image_sent_7= ImageTk.PhotoImage(Image.open("Happy.png").resize((90, 90)))
        elif S == "SAD":
            self.image_sent_7= ImageTk.PhotoImage(Image.open("Sad.png").resize((90, 90)))
        elif S == "EXS":
            self.image_sent_7=  ImageTk.PhotoImage(Image.open("V_Sad.png").resize((90, 90)))
        else:
            self.image_sent_7=  ImageTk.PhotoImage(Image.open("Moderate_Average.png").resize((90, 90)))

        self.man7_img = tk.Label(self, image= self.image_sent_7)
        self.man7_img.place(x= 240, y= 160)
        self.man7_id = tk.Label(self, text= "124")
        self.man7_id.place(x= 270, y= 260)

        # sent_image(self, "201")
        S= boss_df.loc[boss_df["EMPLOYEE_ID"].values == 201]["SENTIMENTS"].values[0]
        if S == "EXH":
            self.image_sent_8= ImageTk.PhotoImage(Image.open("V_Happy.png").resize((90, 90)))
        elif S == "HAP":
            self.image_sent_8= ImageTk.PhotoImage(Image.open("Happy.png").resize((90, 90)))
        elif S == "SAD":
            self.image_sent_8= ImageTk.PhotoImage(Image.open("Sad.png").resize((90, 90)))
        elif S == "EXS":
            self.image_sent_8=  ImageTk.PhotoImage(Image.open("V_Sad.png").resize((90, 90)))
        else:
            self.image_sent_8=  ImageTk.PhotoImage(Image.open("Moderate_Average.png").resize((90, 90)))

        self.man8_img = tk.Label(self, image= self.image_sent_8)
        self.man8_img.place(x= 345, y= 160) 
        self.man8_id = tk.Label(self, text= "201")
        self.man8_id.place(x= 375, y= 260)     

root = tk.Tk()
root.title("Feedback Review")
ico= tk.PhotoImage(file= "ico.png")
root.iconphoto(False, ico)
MainWindow(root)
root.mainloop()