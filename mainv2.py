# a code that searches google for a given query, and opens each link, waits for the simplify popup, presses it, reads the job description, and answers all remaining questions
# on the page with the context of the description and the users resume

# import libraries
from time import sleep
from selenium import common
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from langchain.llms import GPT4All
from langchain.chains import RetrievalQA
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from pdf2image.pdf2image import convert_from_path
# from rake_nltk import Rake
import en_core_web_sm
import glob
import yaml

# load config variables from config.yml
config = yaml.safe_load(open("config.yml"))


def setup_browser():
    # define the path to the chromedriver executable
    driver_path = config["driver_path"]

    b_path = driver_path

    # define the path to the user profile
    userpp = r"C:\Users\thewa\AppData\Local\BraveSoftware\Brave-Browser-Nightly\User Data"
    options = webdriver.ChromeOptions()
    options.binary_location = b_path

    # set dl options
    # prefs = {"download.default_directory": "C:/Users/thewa/Desktop/"}
    # e.g. C:\Users\You\AppData\Local\Google\Chrome\User Data

    userD = f"--user-data-dir={userpp}"
    options.add_argument(userD)
    options.add_argument(r'--profile-directory=Default')  # e.g. Profile 3
    # options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("detach", True)
    browser = webdriver.Chrome(
        executable_path=ChromeDriverManager().install(), options=options)

    return browser


def searchLinks(browser: webdriver.Chrome, scrolls: int = 3, inBatches = False):
    # navigate to Google and search for the query
    close_all_tabs(browser)
    query = config["query"] + " site:boards.greenhouse.io/*/jobs"
    browser.get("https://www.google.com/")
    search_tab = browser.title
    search_box = browser.find_element(By.NAME, "q")
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

    # scroll down, wait for the search results to load, then scroll again
    for _ in range(scrolls):
        browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        sleep(1)

    links = WebDriverWait(browser, 1).until(
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
        batch_size = config["batch_size"]
        batches = [parsed_links[i:i + batch_size]
                for i in range(0, len(parsed_links), batch_size)]
    
    if inBatches: return batches 
    else: return parsed_links


def openLinks(links: list, browser: webdriver.Chrome):
    browser._switch_to.window(browser.window_handles[0])
    for link in links:
        browser.execute_script("window.open('" + link + "', '_blank');")


def simplify(browser: webdriver.Chrome):

    return ""


def getJobDescKeys(job_desc: str):
    nlp = en_core_web_sm.load()
    keys = nlp(job_desc)
    job_desc_keys = str([token.text for token in keys.ents])
    job_desc_keys = job_desc_keys.strip("[],")


def fillApps(browser: webdriver.Chrome, links: list[list], model=None, inBatches: bool = False):
    # switch to the opened tabs
    try:  # not accounting search tab
        if inBatches:
            for idx, batch in enumerate(links):
                openLinks(batch, browser=browser)
                for window_handle in browser.window_handles[idx*len(batch):-1]:
                    doApp(browser, window_handle, model=model)
                    next_apps = input(
                        "Press enter to continue to next batch of apps: ")
                    close_all_tabs(browser)
        else:#default
            openLinks(links, browser=browser)
            for window_handle in browser.window_handles[1:]:
                doApp(browser, window_handle, model=model)
        # close all individual open tabs
        browser.execute_script("alert('All done!')")   
        while True:
            # wait for user input q
            if input("Press q to quit: ") == "q":
                close_all_tabs(browser)
                break
    except KeyboardInterrupt:
        close_all_tabs(browser)


def doApp(browser: webdriver.Chrome, window_handle: str, model: GPT4All):
    browser.switch_to.window(window_handle)
    # wait for simplify popup to load
    sleep(1)
    # get company name from url
    company = browser.current_url.replace(
        "https://boards.greenhouse.io/", "").split("/")[0]
    # if the popup is present, press it
    try:
        # button is in shadow-root and has id fill-button
        browser.execute_script(
            '''return document.querySelector("#simplifyJobsContainer > span").shadowRoot.querySelector("#fill-button").click()''')
        if model is not None:
            resume = load_pdf()
            llm_pass(browser, model, company, resume)
        else:
            try:
                submit = browser.find_element(By.ID, "submit_app")
                submit.click()
            except common.NoSuchElementException:
                print("No submit button found")
                browser.close()
                pass
            print(f"done with {company}")

    except common.exceptions.JavascriptException:
        # close tab, no popup
        browser.close()
        pass


def llm_pass(browser: webdriver.Chrome, model: GPT4All, company: str, resume):
    print("Using LLM")
    # find job description
    job_desc = browser.find_element(
        By.ID, "content").text
    print(job_desc)
    # find the key words in the job description
    job_desc_keys = getJobDescKeys(job_desc)

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

    cover_letter = create_cover(
        job_desc_keys=job_desc_keys, model=model, resume="", company=company, db=db, qa=qa)

    # find the custom questions

    print(f"done with {company}")


def close_all_tabs(browser: webdriver.Chrome):
    for window_handle in browser.window_handles[1:]:
        browser.switch_to.window(window_handle)
        browser.close()
    browser.switch_to.window(browser.window_handles[0])


def load_pdf():

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


def create_cover(job_desc_keys: str, model: GPT4All, resume: str, company: str, db: Chroma, qa):

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


def activateLLM() -> GPT4All:
    # activate LLM from path
    # r"C:\Users\thewa\AppData\Local\nomic.ai\GPT4All4All\ggml-mpt-7b-instruct.bin"
    model = GPT4All(model=config["model_path"], n_ctx=1024, n_batch=1, n_threads=8,
                    n_parts=1, n_predict=1, seed=42, f16_kv=False, logits_all=False, vocab_only=False, use_mlock=False, embedding=False)
    return model if isinstance(model, GPT4All) else None


def main(model=None):
    if model is not None:
        print("LLM is active.")
        print(model)
    scrolls = int(config["scrolls"])
    inBatches = config["inBatches"]
    browser = setup_browser()
    links= searchLinks(browser, scrolls=scrolls)
    fillApps(browser, links, model=model if isinstance(
        model, GPT4All) else None, inBatches=inBatches)


if __name__ == "__main__":
    # define the query to search for
    # check if should use LLM?
    isLLM = config["llm"]

    model = None
    if isLLM:
        makeCoverLetter = config["cover_letter"]
        print("Activating LLM...")
        model = activateLLM()
        if model is None:
            print("Could not activate LLM. Continuing without LLM...")
        else:
            print("LLM activated successfully.")

    main(model=model if isinstance(model, GPT4All) else None)
