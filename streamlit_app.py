import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(
    page_title="Books Price Analysis Dashboard",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ff7f0e;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .faq-question {
        font-weight: bold;
        color: #2e8b57;
        margin-top: 1rem;
    }
    .faq-answer {
        margin-bottom: 1rem;
        padding-left: 1rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache the books dataset"""
    try:
        df = pd.read_csv("all_books_50_pages.csv")
        # Use the existing Price_Numeric column
        df['Price_Clean'] = df['Price_Numeric']
        return df
    except FileNotFoundError:
        st.error("Dataset file 'all_books_50_pages.csv' not found!")
        return None

def calculate_statistics(prices):
    """Calculate comprehensive price statistics"""
    return {
        'count': len(prices),
        'mean': prices.mean(),
        'median': prices.median(),
        'min': prices.min(),
        'max': prices.max(),
        'std': prices.std(),
        'q25': prices.quantile(0.25),
        'q75': prices.quantile(0.75),
        'iqr': prices.quantile(0.75) - prices.quantile(0.25),
        'range': prices.max() - prices.min()
    }

def create_price_distribution_plot(prices, stats):
    """Create price distribution visualization"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Price Distribution Histogram', 'Box Plot', 
                       'Price Categories', 'Cumulative Distribution'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"type": "pie"}, {"secondary_y": False}]]
    )
    
    # Histogram
    fig.add_trace(
        go.Histogram(x=prices, nbinsx=30, name="Price Distribution", 
                    marker_color='skyblue', opacity=0.7),
        row=1, col=1
    )
    
    # Add mean and median lines to histogram
    fig.add_vline(x=stats['mean'], line_dash="dash", line_color="red", 
                  annotation_text=f"Mean: £{stats['mean']:.2f}", row=1, col=1)
    fig.add_vline(x=stats['median'], line_dash="dash", line_color="green", 
                  annotation_text=f"Median: £{stats['median']:.2f}", row=1, col=1)
    
    # Box Plot
    fig.add_trace(
        go.Box(y=prices, name="Price Range", marker_color='lightcoral'),
        row=1, col=2
    )
    
    # Price Categories Pie Chart
    price_bins = [0, 15, 25, 35, 45, 100]
    price_labels = ['Budget (£0-15)', 'Low (£15-25)', 'Medium (£25-35)', 
                   'High (£35-45)', 'Premium (£45+)']
    price_categories = pd.cut(prices, bins=price_bins, labels=price_labels, include_lowest=True)
    category_counts = price_categories.value_counts()
    
    fig.add_trace(
        go.Pie(labels=category_counts.index, values=category_counts.values,
               name="Price Categories"),
        row=2, col=1
    )
    
    # Cumulative Distribution
    sorted_prices = np.sort(prices)
    cumulative_pct = np.arange(1, len(sorted_prices) + 1) / len(sorted_prices) * 100
    
    fig.add_trace(
        go.Scatter(x=sorted_prices, y=cumulative_pct, mode='lines',
                  name='Cumulative %', line=dict(color='darkblue', width=2)),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=True, title_text="Price Distribution Analysis")
    fig.update_xaxes(title_text="Price (£)", row=1, col=1)
    fig.update_yaxes(title_text="Frequency", row=1, col=1)
    fig.update_yaxes(title_text="Price (£)", row=1, col=2)
    fig.update_xaxes(title_text="Price (£)", row=2, col=2)
    fig.update_yaxes(title_text="Cumulative %", row=2, col=2)
    
    return fig

def create_top_books_plot(df):
    """Create top and bottom priced books visualization"""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Top 10 Most Expensive Books', 'Top 10 Cheapest Books'),
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )
    
    # Most expensive books
    top_expensive = df.nlargest(10, 'Price_Clean')
    fig.add_trace(
        go.Bar(y=[title[:30] + '...' if len(title) > 30 else title for title in top_expensive['Title']],
               x=top_expensive['Price_Clean'],
               orientation='h',
               name='Expensive',
               marker_color='coral',
               text=[f'£{price:.2f}' for price in top_expensive['Price_Clean']],
               textposition='outside'),
        row=1, col=1
    )
    
    # Cheapest books
    top_cheap = df.nsmallest(10, 'Price_Clean')
    fig.add_trace(
        go.Bar(y=[title[:30] + '...' if len(title) > 30 else title for title in top_cheap['Title']],
               x=top_cheap['Price_Clean'],
               orientation='h',
               name='Cheap',
               marker_color='lightgreen',
               text=[f'£{price:.2f}' for price in top_cheap['Price_Clean']],
               textposition='outside'),
        row=1, col=2
    )
    
    fig.update_layout(height=600, showlegend=False, title_text="Top and Bottom Priced Books")
    fig.update_xaxes(title_text="Price (£)")
    
    return fig

def main():
    # Main header
    st.markdown('<h1 class="main-header">Books Price Analysis Dashboard</h1>', 
                unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Sidebar
    st.sidebar.header("Navigation")
    
    # Sidebar filters
    st.sidebar.markdown("### Filters")
    
    # Price range filter
    min_price = float(df['Price_Clean'].min())
    max_price = float(df['Price_Clean'].max())
    price_range = st.sidebar.slider(
        "Price Range (£)",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price),
        step=0.01
    )
    
    # Filter data based on price range
    filtered_df = df[(df['Price_Clean'] >= price_range[0]) & 
                     (df['Price_Clean'] <= price_range[1])]
    
    # Display filter info
    st.sidebar.markdown(f"**Showing {len(filtered_df):,} of {len(df):,} books**")
    
    # Navigation options
    page_options = [
        "Overview & Statistics",
        "Price Analysis",
        "Top & Bottom Books",
        "Dataset Explorer",
        "FAQ"
    ]
    
    selected_page = st.sidebar.selectbox("Select Page", page_options)
    
    # Page content
    if selected_page == "Overview & Statistics":
        show_overview(filtered_df)
    elif selected_page == "Price Analysis":
        show_price_analysis(filtered_df)
    elif selected_page == "Top & Bottom Books":
        show_top_bottom_books(filtered_df)
    elif selected_page == "Dataset Explorer":
        show_dataset_explorer(filtered_df)
    elif selected_page == "FAQ":
        show_faq()

def show_overview(df):
    st.markdown('<h2 class="section-header">Dataset Overview</h2>', unsafe_allow_html=True)
    
    # Calculate statistics
    prices = df['Price_Clean']
    stats = calculate_statistics(prices)
    
    # Key metrics in columns
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Books", f"{stats['count']:,}")
    with col2:
        st.metric("Average Price", f"£{stats['mean']:.2f}")
    with col3:
        st.metric("Median Price", f"£{stats['median']:.2f}")
    with col4:
        st.metric("Min Price", f"£{stats['min']:.2f}")
    with col5:
        st.metric("Max Price", f"£{stats['max']:.2f}")
    
    st.markdown("---")
    
    # Detailed statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Basic Statistics")
        stats_df = pd.DataFrame({
            'Statistic': ['Count', 'Mean', 'Median', 'Standard Deviation', 'Minimum', 'Maximum'],
            'Value': [f"{stats['count']:,}", f"£{stats['mean']:.2f}", f"£{stats['median']:.2f}",
                     f"£{stats['std']:.2f}", f"£{stats['min']:.2f}", f"£{stats['max']:.2f}"]
        })
        st.dataframe(stats_df, use_container_width=True)
    
    with col2:
        st.markdown("### Percentiles")
        percentiles_df = pd.DataFrame({
            'Percentile': ['25th', '50th (Median)', '75th', 'IQR'],
            'Value': [f"£{stats['q25']:.2f}", f"£{stats['median']:.2f}",
                     f"£{stats['q75']:.2f}", f"£{stats['iqr']:.2f}"]
        })
        st.dataframe(percentiles_df, use_container_width=True)
    
    # Key insights
    st.markdown("### Key Insights")
    st.write(f"• 50% of books are priced between £{stats['q25']:.2f} and £{stats['q75']:.2f}")
    st.write(f"• Price variation (standard deviation) is £{stats['std']:.2f} ({stats['std']/stats['mean']*100:.1f}% of mean)")
    st.write(f"• The most expensive book costs {stats['max']/stats['min']:.1f}x more than the cheapest")
    st.write(f"• Total price range spans £{stats['range']:.2f}")

def show_price_analysis(df):
    st.markdown('<h2 class="section-header">Price Distribution Analysis</h2>', unsafe_allow_html=True)
    
    prices = df['Price_Clean']
    stats = calculate_statistics(prices)
    
    # Create and display the main visualization
    fig = create_price_distribution_plot(prices, stats)
    st.plotly_chart(fig, use_container_width=True)
    
    # Price categories breakdown
    st.markdown("### Price Categories Breakdown")
    
    price_bins = [0, 15, 25, 35, 45, 100]
    price_labels = ['Budget (£0-15)', 'Low (£15-25)', 'Medium (£25-35)', 
                   'High (£35-45)', 'Premium (£45+)']
    price_categories = pd.cut(prices, bins=price_bins, labels=price_labels, include_lowest=True)
    category_counts = price_categories.value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        category_df = pd.DataFrame({
            'Category': category_counts.index,
            'Count': category_counts.values,
            'Percentage': [f"{(count/len(prices)*100):.1f}%" for count in category_counts.values]
        })
        st.dataframe(category_df, use_container_width=True)
    
    with col2:
        # Simple bar chart for categories
        fig_cat = px.bar(
            x=category_counts.values,
            y=category_counts.index,
            orientation='h',
            title="Books by Price Category",
            labels={'x': 'Number of Books', 'y': 'Price Category'},
            color=category_counts.values,
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig_cat, use_container_width=True)

def show_top_bottom_books(df):
    st.markdown('<h2 class="section-header">Top & Bottom Priced Books</h2>', unsafe_allow_html=True)
    
    # Create visualization
    fig = create_top_books_plot(df)
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Most Expensive Books")
        top_expensive = df.nlargest(15, 'Price_Clean')[['Title', 'Price_Clean']]
        top_expensive['Rank'] = range(1, len(top_expensive) + 1)
        top_expensive = top_expensive[['Rank', 'Title', 'Price_Clean']]
        top_expensive['Price_Clean'] = top_expensive['Price_Clean'].apply(lambda x: f"£{x:.2f}")
        st.dataframe(top_expensive, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("### Cheapest Books")
        top_cheap = df.nsmallest(15, 'Price_Clean')[['Title', 'Price_Clean']]
        top_cheap['Rank'] = range(1, len(top_cheap) + 1)
        top_cheap = top_cheap[['Rank', 'Title', 'Price_Clean']]
        top_cheap['Price_Clean'] = top_cheap['Price_Clean'].apply(lambda x: f"£{x:.2f}")
        st.dataframe(top_cheap, use_container_width=True, hide_index=True)
    
    # Price gap analysis
    st.markdown("### Price Gap Analysis")
    stats = calculate_statistics(df['Price_Clean'])
    expensive_avg = df.nlargest(10, 'Price_Clean')['Price_Clean'].mean()
    cheap_avg = df.nsmallest(10, 'Price_Clean')['Price_Clean'].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Price Range", f"£{stats['range']:.2f}")
    with col2:
        st.metric("Top 10 Average", f"£{expensive_avg:.2f}")
    with col3:
        st.metric("Bottom 10 Average", f"£{cheap_avg:.2f}")
    with col4:
        st.metric("Price Multiplier", f"{stats['max']/stats['min']:.1f}x")

def show_dataset_explorer(df):
    st.markdown('<h2 class="section-header">Dataset Explorer</h2>', unsafe_allow_html=True)
    
    # Search functionality
    search_term = st.text_input("Search books by title:")
    if search_term:
        df = df[df['Title'].str.contains(search_term, case=False, na=False)]
    
    # Display options
    col1, col2 = st.columns(2)
    with col1:
        sort_by = st.selectbox("Sort by:", ['Title', 'Price_Clean', 'Scraped_At'])
    with col2:
        sort_order = st.selectbox("Order:", ['Ascending', 'Descending'])
    
    # Sort data
    ascending = True if sort_order == 'Ascending' else False
    df_sorted = df.sort_values(by=sort_by, ascending=ascending)
    
    # Display dataset
    st.markdown(f"### Dataset ({len(df_sorted):,} books)")
    
    # Format display
    display_df = df_sorted.copy()
    display_df['Price'] = display_df['Price_Clean'].apply(lambda x: f"£{x:.2f}")
    display_df = display_df[['Title', 'Price', 'Scraped_At']]
    
    st.dataframe(display_df, use_container_width=True, height=600)
    
    # Download option
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name="filtered_books_data.csv",
        mime="text/csv"
    )

def show_faq():
    st.markdown('<h2 class="section-header">Frequently Asked Questions</h2>', unsafe_allow_html=True)
    
    faqs = [
        {
            "question": "What is this dataset about?",
            "answer": "This dataset contains 1,000 books scraped from books.toscrape.com, including book titles, prices, and scraping timestamps. The data spans 50 pages of the website and represents a diverse collection of books with various price points."
        },
        {
            "question": "How was the data collected?",
            "answer": "The data was collected using web scraping techniques with Python. The scraper visited 50 pages of the books.toscrape.com website and extracted book information including titles and prices. All prices were cleaned and converted to numeric format for analysis."
        },
        {
            "question": "What is the price range of books in this dataset?",
            "answer": f"Books in this dataset range from £{load_data()['Price_Clean'].min():.2f} to £{load_data()['Price_Clean'].max():.2f}, with an average price of £{load_data()['Price_Clean'].mean():.2f}."
        },
        {
            "question": "What do the price categories mean?",
            "answer": "Books are categorized into 5 price segments: Budget (£0-15) for affordable reads, Low (£15-25) for standard paperbacks, Medium (£25-35) for regular hardcovers, High (£35-45) for premium books, and Premium (£45+) for collector's editions or specialized titles."
        },
        {
            "question": "How accurate is this price analysis?",
            "answer": "The analysis is based on the scraped data from a single point in time. Prices on e-commerce sites can change frequently, so this represents a snapshot of the pricing at the time of data collection. The statistical analysis provides reliable insights into the price distribution patterns."
        },
        {
            "question": "Can I use this data for my own analysis?",
            "answer": "Yes! This is sample data from a demo bookstore website designed for learning web scraping. You can download the filtered data using the download button in the Dataset Explorer section and perform your own analysis."
        },
        {
            "question": "What insights can I get from this analysis?",
            "answer": "The analysis reveals pricing patterns, market segmentation, price distribution characteristics, and helps identify outliers. You can understand how books are priced across different categories and find the most and least expensive options in the dataset."
        },
        {
            "question": "How do I interpret the visualizations?",
            "answer": "The histogram shows price frequency distribution, the box plot reveals quartiles and outliers, the pie chart shows category proportions, and the cumulative distribution shows what percentage of books fall below any given price point."
        }
    ]
    
    for i, faq in enumerate(faqs, 1):
        with st.expander(f"Q{i}: {faq['question']}"):
            st.write(faq['answer'])

if __name__ == "__main__":
    main()
