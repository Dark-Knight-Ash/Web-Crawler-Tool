import streamlit as st
import json
import pandas as pd
import io
import time
from crawler import get_all_links
from collections import Counter

# Styling
st.markdown("""
    <style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        font-size: 16px;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #388E3C;
        transform: scale(1.05);
    }
    .download-btn {
        background-color: #007BFF;
        color: white;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        transition: 0.3s;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Select a view", [
    "🕸️ Crawler Tool",
    "📊 Parameter Frequency Chart",
    "🧠 Crawl Summary Box",
    "🗂️ Crawl History Viewer",
    "🧪 Test URL Preview",
    "⏱️ Crawl Timer"
])

# Session memory
if "history" not in st.session_state:
    st.session_state.history = []
if "start_time" not in st.session_state:
    st.session_state.start_time = None

# Page: Crawler Tool
if page == "🕸️ Crawler Tool":
    st.title("🕷️ Web Crawler Tool")
    url = st.text_input("🔗 Website URL", placeholder="https://example.com")
    max_pages = st.slider("🔢 Max pages to crawl", min_value=5, max_value=50, value=20)

    if st.button("🚀 Start Crawling"):
        if not url:
            st.warning("Please enter a valid URL.")
        else:
            st.session_state.start_time = time.time()
            with st.spinner("Crawling..."):
                result = get_all_links(url, max_pages)
                elapsed = round(time.time() - st.session_state.start_time, 2)
                if result:
                    st.session_state.crawled_data = result
                    st.session_state.history.append((url, result))
                    st.success(f"✅ Found {len(result)} URLs in {elapsed} seconds")
                else:
                    st.error("❌ Crawl failed or no URLs found.")

    # Display crawled data
    if "crawled_data" in st.session_state:
        result = st.session_state.crawled_data

        st.subheader("🔎 Filter Results")
        choice = st.radio("Display:", ["All URLs", "Only URLs with Parameters"])
        filtered = {u: p for u, p in result.items() if (p if choice == "Only URLs with Parameters" else True)}

        # Convert to DataFrame
        data = []
        for link, params in filtered.items():
            if params:
                for key, val in params.items():
                    data.append({"URL": link, "Parameter": key, "Value": val})
            else:
                data.append({"URL": link, "Parameter": "", "Value": ""})
        df = pd.DataFrame(data)

        st.dataframe(df)

        # Downloads
        st.download_button("📥 Download JSON", json.dumps(filtered, indent=2), "filtered_output.json", "application/json")
        st.download_button("📥 Download CSV", df.to_csv(index=False).encode("utf-8"), "filtered_output.csv", "text/csv")

# Page: Parameter Frequency Chart
elif page == "📊 Parameter Frequency Chart":
    st.title("📊 Parameter Frequency")
    if "crawled_data" in st.session_state:
        all_params = []
        for p in st.session_state.crawled_data.values():
            all_params.extend(p.keys())
        param_count = Counter(all_params)
        if param_count:
            df_freq = pd.DataFrame(param_count.items(), columns=["Parameter", "Frequency"])
            st.bar_chart(df_freq.set_index("Parameter"))
        else:
            st.info("No parameters found.")
    else:
        st.info("Please crawl a website first.")

# Page: Crawl Summary
elif page == "🧠 Crawl Summary Box":
    st.title("🧠 Summary")
    if "crawled_data" in st.session_state:
        total = len(st.session_state.crawled_data)
        with_params = sum(1 for v in st.session_state.crawled_data.values() if v)
        all_keys = [k for p in st.session_state.crawled_data.values() for k in p]
        common = Counter(all_keys).most_common(3)
        st.metric("🔗 Total URLs", total)
        st.metric("📌 With Parameters", with_params)
        st.markdown("🔥 **Top Parameters:**")
        for p, c in common:
            st.write(f"- `{p}` used **{c}x**")
    else:
        st.info("No data available.")

# Page: Crawl History
elif page == "🗂️ Crawl History Viewer":
    st.title("📁 Crawl History")
    if st.session_state.history:
        for i, (url, data) in enumerate(reversed(st.session_state.history), 1):
            st.markdown(f"**{i}.** `{url}` - {len(data)} URLs")
    else:
        st.info("No previous crawl history.")

# Page: URL Preview
elif page == "🧪 Test URL Preview":
    st.title("🧪 Preview URLs")
    if "crawled_data" in st.session_state:
        for u in list(st.session_state.crawled_data.keys())[:10]:
            st.markdown(f"[🔗 {u}]({u})", unsafe_allow_html=True)
    else:
        st.info("No URLs to preview.")

# Page: Crawl Timer
elif page == "⏱️ Crawl Timer":
    st.title("⏱️ Time Tracker")
    if st.session_state.start_time:
        elapsed = round(time.time() - st.session_state.start_time, 2)
        st.metric("Elapsed Time", f"{elapsed} sec")
    else:
        st.info("Start a crawl to see timer.")
