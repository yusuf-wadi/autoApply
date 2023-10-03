# a code that searches google for a given query, and opens each link, waits for the simplify popup, presses it, reads the job description, and answers all remaining questions
# on the page with the context of the description and the users resume

# import libraries
from time import sleep
from selenium import common
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains as Actions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from langchain.llms import GPT4All
from langchain.chains import RetrievalQA
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from pdf2image.pdf2image import convert_from_path
# ====#
# from rake_nltk import Rake
import en_core_web_sm
import glob
import yaml
from langchain import OpenAI
import os
import requests
import base64
# ====#


class AutoApplier:
    # load self.config variables from self.config.yml
    def __init__(self, config: dict, profile: dict):

        self.config = config
        self.profile = profile
        self.resume = os.path.normpath(
            os.getcwd() + "/resume/" + self.profile["resume"] + ".pdf")
        self.browser = None

    # ====#

    def setup_browser(self):
        # define the path to the chromedriver executable
        driver_path = self.config["driver_path"]

        b_path = driver_path

        # define the path to the user profile
        userpp = self.config["user_profile"]
        options = webdriver.Chrome or webdriver.FirefoxOptions()
        options.binary_location = b_path

        # set dl options
        # prefs = {"download.default_directory": "C:/Users/thewa/Desktop/"}
        # e.g. C:\Users\You\AppData\Local\Google\Chrome\User Data

        userD = f"--user-data-dir={userpp}"
        options.add_argument(userD)
        options.add_argument(r'--profile-directory=Default')  # e.g. Profile 3
        # options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("detach", True)
        self.browser = webdriver.Chrome or webdriver.Firefox(
            executable_path=ChromeDriverManager().install(), options=options)

    def setup_firefox(self):

        self.browser = webdriver.Firefox()

    def searchLinks(self, scrolls: int = 3, inBatches=False):
        # navigate to Google and search for the query
        self.close_all_tabs(self.browser)
        query = self.config["query"] + " site:boards.greenhouse.io/*/jobs"
        self.browser.get("https://www.google.com/")
        search_box = self.browser.find_element(By.NAME, "q")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        # scroll all the way down, wait for the search results to load, then scroll again
        for _ in range(scrolls):
            self.browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            sleep(1)

        links = WebDriverWait(self.browser, 1).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
        # 6 links per batch in parsed_links
        parsed_links = []
        # iterate over the links and open them
        for link in links:
            href = str(link.get_attribute("href"))
            if href.startswith("https://boards.greenhouse.io/"):
                parsed_links.append(href)

        # cut the parsed links into a list of batches
        if inBatches:
            batch_size = self.config["batch_size"]
            batches = [parsed_links[i:i + batch_size]
                       for i in range(0, len(parsed_links), batch_size)]

        if inBatches:
            return batches
        else:
            return parsed_links

    def linksFromLink(self, link: str):
        self.browser.get(link)
        sleep(1)
        links = WebDriverWait(self.browser, 1).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
        # 6 links per batch in parsed_links
        parsed_links = []
        # iterate over the links and open them
        for link in links:
            href = str(link.get_attribute("href"))
            if href.startswith("https://boards.greenhouse.io/"):
                parsed_links.append(href)
        return parsed_links

    def openLinks(self, links: list):
        """
        opens a list of links given a webdriver
        returns None
        """
        self.browser._switch_to.window(self.browser.window_handles[0])
        for link in links:
            self.browser.execute_script(
                "window.open('" + link + "', '_blank');")

    def focusElement(self, element: webdriver.Chrome or webdriver.Firefox):
        """
        focuses an element given a webdriver
        returns None
        """
        self.browser.execute_script("arguments[0].scrollIntoView();", element)

    def selectDropGreen(self, field: webdriver.Firefox, value):
        """
        selects an option from a dropdown given a webdriver
        returns None
        specifically for greenhouse.io
        whoever made that site is sorry
        """
        value = f"\"{value}\""

        select = field.find_element(By.TAG_NAME, "select")
        select_id = select.get_attribute("id")
        vis_text = field.find_element(By.CLASS_NAME, "select2-chosen")
        vis_text_id = vis_text.get_attribute("id")
        try:
            self.browser.execute_script(
                f"document.getElementById(\"{select_id}\").value = {value};")

            # choose the option thats value attribute is equal to the value
            self.browser.execute_script(
                f"document.getElementById(\"{vis_text_id}\").textContent = Array.from(\
                                                                            document.getElementById(\"{select_id}\").\
                                                                                getElementsByTagName(\"option\")).\
                                                                                    filter(option => option.getAttribute(\"value\") == {value})[0]\
                                                                                        .textContent;")

            sleep(0.5)

        except common.exceptions.JavascriptException:
            print("JavascriptException")
            pass

    def simplify(self):
        sleep(1)
        application = self.browser.find_element(By.ID, "application_form")
        main_fields = application.find_element(
            By.ID, "main_fields").find_elements(By.CLASS_NAME, "field")
        custom_fields = application.find_element(
            By.ID, "custom_fields").find_elements(By.CLASS_NAME, "field")
        eeoc_fields = application.find_element(
            By.ID, "eeoc_fields").find_elements(By.CLASS_NAME, "field")

        # main_fields
        for i in range(len(main_fields)):
            field = main_fields[i]
            self.focusElement(field)
            match(i):
                case 0:
                    # first name
                    field.find_element(By.TAG_NAME, "input").send_keys(
                        self.profile["fname"])
                case 1:
                    # last name
                    field.find_element(By.TAG_NAME, "input").send_keys(
                        self.profile["lname"])
                case 2:
                    # email
                    field.find_element(By.TAG_NAME, "input").send_keys(
                        self.profile["email"])
                case 3:
                    # phone
                    field.find_element(By.TAG_NAME, "input").send_keys(
                        self.profile["phone"])
                case 4:
                    # resume
                    sleep(1)
                    form = self.browser.find_element(
                        By.XPATH, '//*[@id="s3_upload_for_resume"]')
                    form.find_element(By.NAME, "file").send_keys(self.resume)
                    # form.submit()
                case 5:
                    # cover letter
                    sleep(1)
                    cover_letter_path = os.path.normpath(
                        os.getcwd() + "/cover_letters/" + "temp" + ".txt")
                    form = self.browser.find_element(
                        By.XPATH, '//*[@id="s3_upload_for_cover_letter"]')
                    form.find_element(By.NAME, "file").send_keys(
                        cover_letter_path)
                    # form.submit()
                case _:
                    # raise(Warning("How did you get here"))
                    pass

        # custom_fields
        for field in custom_fields:
            # determine question type
            question_type = field.find_element(By.TAG_NAME, "label").text
            self.focusElement(field)
            match(question_type):
                case _ if "LinkedIn" in question_type:

                    field.find_elements(
                        By.TAG_NAME, "input")[-1].send_keys(self.profile["linkedin"])
                case _ if "Website" in question_type:
                    field.find_elements(
                        By.TAG_NAME, "input")[-1].send_keys(self.profile["website"])
                case [*_, "GitHub"]:
                    field.find_elements(
                        By.TAG_NAME, "input")[-1].send_keys(self.profile["github"])
                case _ if "visa status" in question_type:
                    if self.profile["visa"]:
                        self.selectDropGreen(field, 1)
                    else:
                        self.selectDropGreen(field, 0)
                case _:
                    # raise(Warning("How did you get here"))
                    pass
        # eeoc_fields
        for i in range(len(eeoc_fields)):
            field = eeoc_fields[i]
            display_name = field.find_element(By.TAG_NAME, "label").text
            self.focusElement(field)
            match(display_name):
                case _ if "Gender" in display_name:
                    # gender
                    if self.profile["gender"]:
                        self.selectDropGreen(field, 1)
                    else:
                        self.selectDropGreen(field, 2)
                    pass
                case _ if "Hispanic" in display_name:
                    # hispanic or latino
                    if self.profile["hispanic"]:
                        self.selectDropGreen(field, "Yes")
                    else:
                        self.selectDropGreen(field, "No")

                case _ if "Veteran" in display_name:
                    # veteran status
                    if self.profile["veteran"]:
                        self.selectDropGreen(field, 2)
                    else:

                        self.selectDropGreen(field, 1)
                case _ if "Disability" in display_name:
                    # disability status
                    if self.profile["disabled"]:
                        self.selectDropGreen(field, 1)
                    else:
                        self.selectDropGreen(field, 2)
                case _:
                    # raise(Warning("How did you get here"))
                    pass

    def getJobDescKeys(self, job_desc: str):
        nlp = en_core_web_sm.load()
        keys = nlp(job_desc)
        job_desc_keys = str([token.text for token in keys.ents])
        job_desc_keys = job_desc_keys.strip("[],")

    def fillApps(self, links: list[list], model=None, inBatches: bool = False):
        # switch to the opened tabs
        try:  # not accounting search tab
            if inBatches:
                for idx, batch in enumerate(links):
                    self.openLinks(batch)
                    for window_handle in self.browser.window_handles[idx*len(batch):-1]:
                        self.doApp(window_handle, model=model)
                    next_apps = input(
                        "Press enter to continue to next batch of apps: ")
                    self.close_all_tabs(self.browser)
            else:  # default
                self.openLinks(links)
                for window_handle in self.browser.window_handles[1:]:
                    self.doApp(window_handle, model=model)
            # close all individual open tabs
            self.browser.execute_script("alert('All done!')")
            while True:
                # wait for user input q
                if input("Press q to quit: ") == "q":
                    self.close_all_tabs(self.browser)
                    break
        except KeyboardInterrupt:
            self.close_all_tabs(self.browser)

    def doApp(self, window_handle: str, model=None):
        self.browser.switch_to.window(window_handle)
        # wait for simplify popup to load
        sleep(1)
        # get company name from url
        company = self.browser.current_url.replace(
            "https://boards.greenhouse.io/", "").split("/")[0]
        # if the popup is present, press it
        try:
            # button is in shadow-root and has id fill-button
            # self.browser.execute_script(
            #     '''return document.querySelector("#simplifyJobsContainer > span").shadowRoot.querySelector("#fill-button").click()''')
            self.simplify()
            if model is not None:
                resume = self.load_pdf()
                self.llm_pass(model, company, resume)
            else:
                try:
                    submit = self.browser.find_element(By.ID, "submit_app")
                    submit.click()
                except common.NoSuchElementException:
                    print("No submit button found")
                    self.browser.close()
                    pass
                print(f"done with {company}")

        except common.exceptions.JavascriptException:
            # close tab, no popup
            self.browser.close()
            pass

    def llm_pass(self, model: GPT4All, company: str, resume):
        print("Using LLM")
        # find job description
        job_desc = self.browser.find_element(
            By.ID, "content").text
        print(job_desc)
        # find the key words in the job description
        job_desc_keys = self.getJobDescKeys(job_desc)

        print(job_desc_keys)

        # make cover letter
        if resume is None:
            print("No resume found")
            return None

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024,
            chunk_overlap=64
        )
        texts = text_splitter.split_documents(resume)
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        db = Chroma.from_documents(
            texts, embeddings, persist_directory="db")
        qa = RetrievalQA.from_chain_type(
            llm=model,
            chain_type="stuff",
            retriever=db.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True,
            verbose=False,
        )
        ###

        cover_letter = self.create_cover(
            job_desc_keys=job_desc_keys, model=model, resume="", company=company, db=db, qa=qa)

        # find the custom questions

        print(f"done with {company}")

    def close_all_tabs(self,):
        for window_handle in self.browser.window_handles[1:]:
            self.browser.switch_to.window(window_handle)
            self.browser.close()
        self.browser.switch_to.window(self.browser.window_handles[0])

    def load_pdf(self):

        pdf_files = glob.glob("resume/*.pdf")

        if pdf_files:
            first_pdf = pdf_files[0]
            # do something with the first PDF file here
        else:
            print("No PDF files found in the resume directory.")
            return None
        loader = PyPDFLoader(first_pdf)
        document = loader.load_and_split()

        return document

    def create_cover(self, job_desc_keys: str, model: GPT4All, resume: str, company: str, db: Chroma, qa):

        role = "Software Engineer"
        prompt = f"Job Description Key Words: {job_desc_keys}\n\n Corressponding Cover Letter for {role} at {company} from applicant:\n\n"
        print(prompt)
        print("Generating cover letter...")
        cover_letter = qa(prompt)
        # write to file in cover_letters folder
        with open(f"cover_letters/{company}_cover_letter.txt", "w") as f:
            for line in cover_letter.split("\n"):
                f.write(f"{line}\n")

        # wait for user input (testing purposes)
        ###

        return cover_letter

    def activateLocalLM(self) -> GPT4All:
        # activate LLM from path
        # r"C:\Users\thewa\AppData\Local\nomic.ai\GPT4All4All\ggml-mpt-7b-instruct.bin"
        model = GPT4All(model=self.config["model_path"], n_ctx=1024, n_batch=1, n_threads=8,
                        n_parts=1, n_predict=1, seed=42, f16_kv=False, logits_all=False, vocab_only=False, use_mlock=False, embedding=False)
        return model if isinstance(model, GPT4All) else None

    def main(self, model=None):
        if model is not None:
            print("LLM is active.")
            print(model)
        scrolls = int(self.config["scrolls"])
        inBatches = self.config["inBatches"]
        self.browser = self.setup_self.browser()
        links = self.searchLinks(self.browser, scrolls=scrolls)
        self.fillApps(self.browser, links, model=model if isinstance(
            model, GPT4All) else None, inBatches=inBatches)