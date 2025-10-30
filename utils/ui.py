import streamlit as st


def inject_global_css():
	"""Injects global CSS for a modern, cohesive look across all pages."""
	css = """
	<style>
	:root {
		--brand: #1DB954; /* Spotify green */
		--brand-dark: #169c45;
		--bg-grad-top: #0f2027;
		--bg-grad-mid: #203a43;
		--bg-grad-bot: #2c5364;
		--card-bg: rgba(255,255,255,0.06);
		--card-border: rgba(255,255,255,0.12);
		--text: #f4f7f8;
	}

	/* Background gradient */
	.stApp {
		background: linear-gradient(135deg, var(--bg-grad-top), var(--bg-grad-mid) 50%, var(--bg-grad-bot));
		color: var(--text);
	}

	/* Make headers bolder and spaced */
	h1, h2, h3, h4 { color: var(--text) !important; }
	h1 {
		letter-spacing: 0.5px;
	}

	/* Card-like containers */
	.block-container { padding-top: 2rem !important; }
	.card {
		background: var(--card-bg);
		border: 1px solid var(--card-border);
		border-radius: 16px;
		padding: 22px 24px;
		margin-bottom: 20px;
		backdrop-filter: blur(8px);
		-webkit-backdrop-filter: blur(8px);
		transition: transform 120ms ease, box-shadow 120ms ease, border-color 120ms ease;
	}
	.card:hover { transform: translateY(-2px); border-color: rgba(255,255,255,0.22); }

	/* Buttons */
	.stButton > button {
		background: var(--brand);
		color: #0b0f10;
		border-radius: 10px;
		border: none;
		font-weight: 600;
		padding: 0.6rem 1rem;
	}
	.stButton > button:hover { background: var(--brand-dark); }

	/* Inputs */
	.stSelectbox, .stMultiSelect, .stTextInput { color: #0b0f10; }

	/* Tables */
	.dataframe, .stTable { border-radius: 10px; overflow: hidden; }

	/* Metrics */
	[data-testid="stMetricValue"] { color: var(--brand) !important; }

	/* Footer */
	.footer { text-align: center; opacity: 0.85; margin-top: 1rem; }
	</style>
	"""
	st.markdown(css, unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str | None = None, emoji: str | None = None):
	"""Renders a consistent page header with optional subtitle and emoji."""
	heading = f"{emoji} {title}" if emoji else title
	st.markdown(f"<div class='card' style='padding: 24px; margin-bottom: 8px;'>\n<h1 style='margin: 0;'>{heading}</h1>\n{f'<p style=\"margin: 6px 0 0; opacity: .9;\">{subtitle}</p>' if subtitle else ''}\n</div>", unsafe_allow_html=True)


def card(title: str | None = None):
	"""Context manager to place content in a styled card."""
	class _Card:
		def __enter__(self):
			st.markdown("<div class='card'>", unsafe_allow_html=True)
			if title:
				st.markdown(f"**{title}**")
			return self
		def __exit__(self, exc_type, exc, tb):
			st.markdown("</div>", unsafe_allow_html=True)
	return _Card()


def footer(text: str):
	st.markdown(f"<div class='footer'>{text}</div>", unsafe_allow_html=True)


