import pandas as pd
from .models import RealEstateData

def load_sample_data():
    try:
        df = pd.read_excel('sample_data/Sample_data.xlsx')
        df = df.fillna(0)

        column_mapping = {
            'final location': 'final_location',
            'total_sales - igr': 'total_sales_igr',
            'total sold - igr': 'total_sold_igr',
            'flat_sold - igr': 'flat_sold_igr',
            'office_sold - igr': 'office_sold_igr',
            'others_sold - igr': 'others_sold_igr',
            'shop_sold - igr': 'shop_sold_igr',
            'commercial_sold - igr': 'commercial_sold_igr',
            'other_sold - igr': 'other_sold_igr',
            'residential_sold - igr': 'residential_sold_igr',
            'flat - weighted average rate': 'flat_weighted_avg_rate',
            'office - weighted average rate': 'office_weighted_avg_rate',
            'others - weighted average rate': 'others_weighted_avg_rate',
            'shop - weighted average rate': 'shop_weighted_avg_rate',
            'flat - most prevailing rate - range': 'flat_prevailing_rate_range',
            'office - most prevailing rate - range': 'office_prevailing_rate_range',
            'others - most prevailing rate - range': 'others_prevailing_rate_range',
            'shop - most prevailing rate - range': 'shop_prevailing_rate_range',
            'total carpet area supplied (sqft)': 'total_carpet_area',
            'total units': 'total_units',
            'flat total': 'flat_total',
            'shop total': 'shop_total',
            'office total': 'office_total',
            'others total': 'others_total'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Delete existing data
        RealEstateData.objects.all().delete()
        
        # Create records
        for _, row in df.iterrows():
            RealEstateData.objects.create(**row.to_dict())
        
        return True, "Data loaded successfully"
    except Exception as e:
        return False, f"Error loading data: {str(e)}"

def generate_summary(df, query):
    areas = df['final_location'].unique()
    avg_price = df['flat_weighted_avg_rate'].mean()
    return f"Analysis for '{query}'. Areas: {', '.join(areas)}. Average price: ₹{avg_price:,.2f} per sqft."

def prepare_chart_data(df, query):
    if 'compare' in query.lower():
        areas = [word for word in query.split() if word.lower() in df['final_location'].str.lower().values]
        if not areas:
            areas = df['final_location'].unique()[:2]
        
        datasets = []
        for area in areas:
            area_data = df[df['final_location'].str.lower() == area.lower()]
            datasets.append({
                'label': area,
                'data': area_data['flat_weighted_avg_rate'].tolist(),
                'borderColor': f'#{hash(area) % 0xFFFFFF:06x}',
            })
        
        return {
            'labels': sorted(df['year'].unique()),
            'datasets': datasets,
            'title': f'Price Comparison: {" vs ".join(areas)}'
        }
    else:
        area = next((word for word in query.split() if word.lower() in df['final_location'].str.lower().values), None)
        if not area:
            area = df['final_location'].iloc[0]
        
        area_data = df[df['final_location'].str.lower() == area.lower()]
        return {
            'labels': area_data['year'].tolist(),
            'datasets': [{
                'label': 'Price',
                'data': area_data['flat_weighted_avg_rate'].tolist(),
                'borderColor': '#4f46e5',
            }],
            'title': f'Price Trend for {area}'
        }

def filter_table_data(df, query):
    if 'compare' in query.lower():
        areas = [word for word in query.split() if word.lower() in df['final_location'].str.lower().values]
        if areas:
            return df[df['final_location'].str.lower().isin([a.lower() for a in areas])]
    else:
        area = next((word for word in query.split() if word.lower() in df['final_location'].str.lower().values), None)
        if area:
            return df[df['final_location'].str.lower() == area.lower()]
    
    return df.head(10)