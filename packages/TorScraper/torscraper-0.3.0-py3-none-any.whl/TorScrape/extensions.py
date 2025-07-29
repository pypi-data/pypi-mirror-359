import random
import time
import socket
import networkx as nx
import matplotlib.pyplot as plt
from selenium.webdriver.common.by import By

# Save full HTML and screenshot
def save_full_html_and_screenshot(driver, html_file='page.html', screenshot_file='screenshot.png'):
    html = driver.page_source
    with open(html_file, 'w') as f:
        f.write(html)
    driver.save_screenshot(screenshot_file)
    print(f"Saved HTML to {html_file} and screenshot to {screenshot_file}")

# Enumerate extra elements (title, metas, forms)
def enumerate_page_elements(driver):
    title = driver.title
    print(f"Page title: {title}")

    metas = driver.find_elements(By.TAG_NAME, 'meta')
    for meta in metas:
        print(f"Meta: {meta.get_attribute('name')} = {meta.get_attribute('content')}")

    forms = driver.find_elements(By.TAG_NAME, 'form')
    print(f"Found {len(forms)} forms on page")

# Print form inputs
def print_form_inputs(driver):
    forms = driver.find_elements(By.TAG_NAME, 'form')
    for i, form in enumerate(forms):
        print(f"\nForm #{i + 1}:")
        inputs = form.find_elements(By.TAG_NAME, 'input')
        for inp in inputs:
            name = inp.get_attribute('name')
            type_ = inp.get_attribute('type')
            print(f"  Input name: {name}, type: {type_}")

# Check for external resources
def check_external_resources(driver):
    resources = driver.find_elements(By.XPATH, '//script|//img|//link')
    for res in resources:
        src = res.get_attribute('src') or res.get_attribute('href')
        if src and not src.endswith('.onion'):
            print(f"External resource found: {src}")

# Crawl links one level deep
def crawl_links(driver, base_url):
    links = driver.find_elements(By.TAG_NAME, 'a')
    crawled = []
    for link in links:
        href = link.get_attribute('href')
        if href and href.startswith(base_url):
            crawled.append(href)
    print(f"Found {len(crawled)} internal links for crawling (one level deep):")
    for link in crawled:
        print(link)
    return crawled

# Build and visualize a graph of links
def build_link_graph(links, base_url):
    G = nx.DiGraph()
    for link in links:
        G.add_edge(base_url, link)
    nx.draw(G, with_labels=True, node_color='lightblue', node_size=1500, font_size=8)
    plt.show()

# Request new Tor circuit
def request_new_tor_circuit():
    try:
        s = socket.socket()
        s.connect(("127.0.0.1", 9051))  # Tor control port
        s.send(b'AUTHENTICATE ""\r\n')
        resp = s.recv(1024)
        if b'250' not in resp:
            print("Authentication failed")
            return
        s.send(b'SIGNAL NEWNYM\r\n')
        resp = s.recv(1024)
        if b'250' in resp:
            print("New Tor circuit requested successfully!")
        else:
            print("Failed to request new circuit.")
    except Exception as e:
        print(f"Error requesting new circuit: {e}")
    finally:
        s.close()

# Randomize user-agent
def random_user_agent():
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    ]
    chosen = random.choice(agents)
    print(f"Selected random User-Agent: {chosen}")
    return chosen

# Stealth delay
def stealth_delay(min_delay=2, max_delay=6):
    t = random.uniform(min_delay, max_delay)
    print(f"Sleeping for {t:.2f} seconds to simulate human behavior...")
    time.sleep(t)
