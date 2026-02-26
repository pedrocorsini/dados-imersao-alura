import streamlit as st
import pandas as pd
import plotly.express as px

# layout        
st.set_page_config(
    page_title='Amazon Sales Dashboard',
    page_icon='resources/amazon-icon.svg', 
    layout='wide',
    initial_sidebar_state='collapsed',
)

# Loading and caching the dataframe

@st.cache_data
def load_data():
    return pd.read_csv('resources/amazon_sales_highly_unbalanced_v3.csv')
df = load_data()

@st.cache_data
def load_data_balanced():
    return pd.read_csv('resources/amazon_sales_dataset.csv')
df_balanced = load_data_balanced()

# Sidebar Filters

st.logo(image='resources/amazon-tile.svg', size='large', link='https://www.amazon.com')

st.sidebar.header('🔎 | Filters')

# Regions

regions_availables = sorted(df['customer_region'].unique())
regions_selected = st.sidebar.pills('Regions', options=regions_availables, selection_mode='multi', default=regions_availables)

# Product Category

categories_availables = sorted(df['product_category'].unique())
categories_selected = st.sidebar.pills('Product Categories', options=categories_availables, selection_mode='multi', default=categories_availables)

# Payment Methods

payments_availables = sorted(set(df['payment_method'].unique()) | set(df_balanced['payment_method'].unique()))
payments_selected = st.sidebar.pills('Payment Methods', options=payments_availables, selection_mode='multi', default=payments_availables)

df['order_year'] = df['order_date'].str[:4]
df_balanced['order_year'] = df_balanced['order_date'].str[:4]
years_availables = sorted(df['order_year'].unique())
years_selected = st.sidebar.pills('Order Years', options=years_availables, selection_mode='multi', default=years_availables)

# Filtring DataFrame

df_filtered = df[
    (df['customer_region'].isin(regions_selected)) &
    (df['product_category'].isin(categories_selected)) &
    (df['payment_method'].isin(payments_selected)) &
    (df['order_year'].isin(years_selected))
]

df_balanced_filtered = df_balanced[
    (df_balanced['customer_region'].isin(regions_selected)) &
    (df_balanced['product_category'].isin(categories_selected)) &
    (df_balanced['payment_method'].isin(payments_selected)) &
    (df_balanced['order_year'].isin(years_selected))    
]

# Page title

col_title1, col_title2 = st.columns([1, 10])

with col_title1:
    st.image('resources/amazon-ar21.svg')

with col_title2:
    st.title( '| Amazon Sales Dashboard')

st.markdown('Explore Amazon Sales Data between 2022 and 2023')
st.markdown('---')

# General Metrics

st.subheader('General Metrics')

if not df_filtered.empty:
    total_sold = df['quantity_sold'].sum()
    revenue = df['total_revenue'].sum()
    lowest = df['price'].min()
    highest = df['price'].max()
else:
    total_sold, revenue, lowest, highest = 0, 0, 0, 0

col1, col2, col3, col4 = st.columns(4)
col1.metric('Total of Items Sold', total_sold)
col2.metric('Total Revenue (USD)', f'${revenue:,.0f}')
col3.metric('Lowest Product Price:', f'${lowest:,.0f}')
col4.metric('Highest Product Price', f'${highest:,.0f}')

st.markdown('---')

# Tabs

tab1, tab2, tab3 = st.tabs(['Graphs', 'Graphs (Balanced Data Frame)','Data Frame'], width='stretch')

# Graphs
with tab1:
    tab1.header('Graphs')
    st.markdown('For better visualization of the graphs, please fullscreen them.')
    col_graph1, col_graph2 = st.columns(2)

    with col_graph1:
        if not df_filtered.empty:
            category_amount_sold = df_filtered.groupby('product_category')['quantity_sold'].sum().reset_index()
            category_pie = px.pie(
                category_amount_sold,
                names='product_category',
                values='quantity_sold',
                hole=0.3,
                color_discrete_sequence=px.colors.qualitative.Antique, 
                title='Pie Graph of Prodcut Categories Sales',
                labels={
                    'product_category' : 'Product Category',
                    'quantity_sold' : 'Quantity Sold'
                }
            )  
            category_pie.update_traces(textinfo='label+value+percent')        
            st.plotly_chart(category_pie, width='stretch')
        else:
            st.warning('There is no data available for this graph')

    with col_graph2:
        if not df_filtered.empty:
            region = df_filtered.groupby('product_category')['customer_region'].value_counts().reset_index()
            fig_region_category = px.histogram(
                region,
                x='customer_region',
                y='count',
                color='product_category',
                text_auto=True,
                barmode='group',
                labels={
                    'count' : 'Count Per Category',
                    'customer_region' : 'Customer Region',
                    'product_category' : 'Product Category'
                },
                color_discrete_sequence=px.colors.qualitative.Antique, 
                title='Product Sales Per Category and Customer Region'
            )
            fig_region_category.update_traces(textangle=0)
            fig_region_category.update_yaxes(title_text='Quantity Sales Per Category')
            st.plotly_chart(fig_region_category, width='stretch')
        else:
            st.warning('There is no data available for this graph')

    col_graph3, col_graph4 = st.columns(2)

    with col_graph3:
        if not df_filtered.empty:
            payment = df_filtered.groupby('product_category')['payment_method'].value_counts().reset_index()
            payment_graph = px.histogram(
                payment,
                x = 'payment_method',
                y = 'count',  
                color = 'product_category',
                text_auto = True,
                barmode = 'group',
                color_discrete_sequence = px.colors.qualitative.Antique, 
                title = 'Payment Method Sales Per Category',    
                labels={
                    'payment_method' : 'Payment Method',
                    'count' : 'Quantity per Sold'
                }    
            )
            payment_graph.update_traces(textangle=0)
            payment_graph.update_yaxes(title_text='Payment Methods Per Category')
            st.plotly_chart(payment_graph, width='stretch')
        else:
            st.warning('There is no data available for this graph')
    
    with col_graph4:
        if not df_filtered.empty:
            payment_region = df_filtered.groupby('customer_region')['payment_method'].value_counts().reset_index()
            payment_region_graph = px.histogram(
                payment_region,
                x = 'customer_region',
                y = 'count',
                color = 'payment_method',
                text_auto=True,
                barmode='group',
                labels={        
                    'customer_region' : 'Customer Region',
                    'payment_method' : 'Payment Method'
                },
                color_discrete_sequence=px.colors.qualitative.Antique, 
                title='Payment Methods per Customer Region'
            )
            payment_region_graph.update_traces(textangle=0)
            payment_region_graph.update_yaxes(title_text='Quantity of the Payment Methods per Region')
            st.plotly_chart(payment_region_graph, width='stretch')
        else:
            st.warning('There is no data available for this graph')

with tab2:
    tab2.header('Graphs (Balanced Data Frame)')
    st.markdown('For better visualization of the graphs, please fullscreen them.')
    col_graph1_tab2, col_graph2_tab2 = st.columns(2)

    with col_graph1_tab2:
        if not df_balanced_filtered.empty:
            category_amount_sold_2 = df_balanced_filtered.groupby('product_category')['quantity_sold'].sum().reset_index()
            category_pie_2 = px.pie(
                category_amount_sold_2,
                names='product_category',
                values='quantity_sold',
                hole=0.3,
                color_discrete_sequence=px.colors.qualitative.Antique, 
                title='Pie Graph of Prodcut Categories Sales',
                labels={
                    'product_category' : 'Product Category',
                    'quantity_sold' : 'Quantity Sold'
                }
            )  
            category_pie_2.update_traces(textinfo='label+value+percent')        
            st.plotly_chart(category_pie_2, width='stretch')
        else:
            st.warning('There is no data available for this graph')

    with col_graph2_tab2:
        if not df_balanced_filtered.empty:
            region_2 = df_balanced_filtered.groupby('product_category')['customer_region'].value_counts().reset_index()
            fig_region_category_2 = px.histogram(
                region_2,
                x='customer_region',
                y='count',
                color='product_category',
                text_auto=True,
                barmode='group',
                labels={
                    'count' : 'Count Per Category',
                    'customer_region' : 'Customer Region',
                    'product_category' : 'Product Category'
                },
                color_discrete_sequence=px.colors.qualitative.Antique, 
                title='Product Sales Per Category and Customer Region'
            )
            fig_region_category_2.update_traces(textangle=0)
            fig_region_category_2.update_yaxes(title_text='Quantity Sales Per Category')
            st.plotly_chart(fig_region_category_2, width='stretch')
        else:
            st.warning('There is no data available for this graph')

    col_graph3_tab2, col_graph4_tab2 = st.columns(2)

    with col_graph3_tab2:
        if not df_balanced_filtered.empty:
            payment_2 = df_balanced_filtered.groupby('product_category')['payment_method'].value_counts().reset_index()
            payment_graph_2 = px.histogram(
                payment_2,
                x = 'payment_method',
                y = 'count',  
                color = 'product_category',
                text_auto = True,
                barmode = 'group',
                color_discrete_sequence = px.colors.qualitative.Antique, 
                title = 'Payment Method Sales Per Category',    
                labels={
                    'payment_method' : 'Payment Method',
                    'count' : 'Quantity per Sold'
                }    
            )
            payment_graph_2.update_traces(textangle=0)
            payment_graph_2.update_yaxes(title_text='Payment Methods Per Category')
            st.plotly_chart(payment_graph_2, width='stretch')
        else:
            st.warning('There is no data available for this graph')
    
    with col_graph4_tab2:
        if not df_balanced_filtered.empty:
            payment_region_2 = df_balanced_filtered.groupby('customer_region')['payment_method'].value_counts().reset_index()
            payment_region_graph_2 = px.histogram(
                payment_region_2,
                x = 'customer_region',
                y = 'count',
                color = 'payment_method',
                text_auto=True,
                barmode='group',
                labels={        
                    'customer_region' : 'Customer Region',
                    'payment_method' : 'Payment Method'
                },
                color_discrete_sequence=px.colors.qualitative.Antique, 
                title='Payment Methods per Customer Region'
            )
            payment_region_graph_2.update_traces(textangle=0)
            payment_region_graph_2.update_yaxes(title_text='Quantity of the Payment Methods per Region')
            st.plotly_chart(payment_region_graph_2, width='stretch')
        else:
            st.warning('There is no data available for this graph')    

with tab3:
    tab3.header('Amazon Sales Complete Data Frame')
    st.dataframe(df_filtered, width='stretch', hide_index=True)

    st.divider()

    tab3.header('Unbalanced Complete Data Frame')
    st.dataframe(df_balanced_filtered, width='stretch', hide_index=True)