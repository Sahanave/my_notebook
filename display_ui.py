import streamlit as st

# Set page config
st.set_page_config(layout="wide", page_title="Claude Agents on Vertex AI")

# Define the layout using columns and containers
with st.container():
    st.markdown("""
        <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
        }
        .slide-box, .video-box, .reference-box, .question-box {
            border: 2px solid #E5E5E5;
            border-radius: 10px;
            padding: 1rem;
            background-color: #F4F0EB;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("Building Agents with Claude on Vertex AI")

    # Split screen: left for slides, right for video
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📑 Slide Placeholder")
        st.markdown("<div class='slide-box'>\nAdd your slides or visuals here.\n</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("### 🎥 Live Video Placeholder")
        st.markdown("<div class='video-box'>\nLive speaker video stream here.\n</div>", unsafe_allow_html=True)

    # References and Question section below
    col3, col4 = st.columns([1, 1])

    with col3:
        st.markdown("### 📚 Reference Links")
        st.markdown("""
            <div class='reference-box'>
            <ul>
                <li><a href='#'>Configure Claude Code on Vertex</a></li>
                <li><a href='#'>Learn more about MCP</a></li>
                <li><a href='#'>Get started with Claude on Vertex AI</a></li>
            </ul>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("### ❓ Ask a Question")
        st.markdown("<div class='question-box'>\nForm for live Q&A interaction.\n</div>", unsafe_allow_html=True)
        user_question = st.text_input("Enter your question:")
        if st.button("Submit"):
            st.success("Your question has been submitted!")
