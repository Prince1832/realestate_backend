from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser
from .models import RealEstateData
import pandas as pd
from .services.openai_service import generate_real_estate_summary


class RealEstateAnalysisView(APIView):
    parser_classes = [JSONParser, MultiPartParser]

    def post(self, request):
        query = request.data.get('query', '').lower()
        use_ai = request.data.get('use_ai', False)

        
        qs = RealEstateData.objects.all()
        data = list(qs.values())
        df = pd.DataFrame(data)

       
        if not self._is_valid_query(df, query):
            return Response({
                'summary': "__error__The location/area you entered is not available in our database",
                'chart_data': None,
                'table_data': []
            })

        # Generate response
        summary = self._generate_summary(df, query, use_ai)
        chart_data = self._prepare_chart_data(df, query)
        table_data = self._filter_table_data(df, query)

        return Response({
            'summary': summary,
            'chart_data': chart_data,
            'table_data': table_data.to_dict('records'),
        })

    def _is_valid_query(self, df, query):
        """Check if query contains valid location names"""
        if 'compare' in query.lower():
            areas = self._extract_areas_from_query(df, query)
            return bool(areas)  
        else:
            area = self._extract_primary_area(df, query)
            return area is not None  

    def _generate_summary(self, df, query, use_ai=True):
        """Generate summary (AI or basic) based on use_ai flag"""
        if use_ai:
            try:
                return generate_real_estate_summary(df, query)
            except Exception as e:
                print(f"OpenAI Error: {e}")

        # Basic summary fallback
        if 'compare' in query.lower():
            areas = self._extract_areas_from_query(df, query) or df['final_location'].unique()[:2]
            summary_parts = []
            for area in areas:
                area_data = df[df['final_location'].str.lower() == area.lower()]
                if not area_data.empty:
                    avg_price = area_data['flat_weighted_avg_rate'].mean()
                    summary_parts.append(f"{area.title()}: ₹{avg_price:,.2f} per sqft")
                else:
                    summary_parts.append(f"{area.title()}: No data")
            return f"Analysis for '{query}'. " + " | ".join(summary_parts)
        else:
            area = self._extract_primary_area(df, query) or df['final_location'].iloc[0]
            area_data = df[df['final_location'].str.lower() == area.lower()]
            if not area_data.empty:
                avg_price = area_data['flat_weighted_avg_rate'].mean()
                return f"Analysis for '{area.title()}': ₹{avg_price:,.2f} per sqft."
            else:
                return f"No data available for '{area}'."

    def _prepare_chart_data(self, df, query):
        
        if 'compare' in query.lower():
            areas = self._extract_areas_from_query(df, query) or df['final_location'].unique()[:2]
            return self._prepare_comparison_chart(df, areas)
        else:
            area = self._extract_primary_area(df, query) or df['final_location'].iloc[0]
            return self._prepare_single_area_chart(df, area)

    def _filter_table_data(self, df, query):
        
        if 'compare' in query.lower():
            areas = self._extract_areas_from_query(df, query)
            if areas:
                return df[df['final_location'].str.lower().isin([a.lower() for a in areas])]
        else:
            area = self._extract_primary_area(df, query)
            if area:
                return df[df['final_location'].str.lower() == area.lower()]
        return df.head(10)

    # Helper methods
    def _extract_areas_from_query(self, df, query):
       
        valid_areas = df['final_location'].str.lower().unique()
        return [word for word in query.split() if word.lower() in valid_areas]

    def _extract_primary_area(self, df, query):
        valid_areas = df['final_location'].str.lower().unique()
        query = query.lower()
        return next((area for area in valid_areas if area in query), None)
    
    def _extract_areas_from_query(self, df, query):
        valid_areas = df['final_location'].str.lower().unique()
        query = query.lower()
        return [area for area in valid_areas if area in query]

    def _prepare_comparison_chart(self, df, areas):
        
        datasets = []
        for area in areas:
            area_data = df[df['final_location'].str.lower() == area.lower()]
            yearly_avg = area_data.groupby('year')['flat_weighted_avg_rate'].mean().sort_index()
            datasets.append({
                'label': area.title(),
                'data': yearly_avg.tolist(),
                'borderColor': f'#{hash(area) % 0xFFFFFF:06x}',
            })

        labels = sorted(df['year'].unique())
        return {
            'labels': labels,
            'datasets': datasets,
            'title': f'Price Comparison: {" vs ".join([a.title() for a in areas])}'
        }

    def _prepare_single_area_chart(self, df, area):
        
        area_data = df[df['final_location'].str.lower() == area.lower()]
        yearly_avg = area_data.groupby('year')['flat_weighted_avg_rate'].mean().sort_index()
        return {
            'labels': yearly_avg.index.tolist(),
            'datasets': [{
                'label': 'Price',
                'data': yearly_avg.tolist(),
                'borderColor': '#4f46e5',
            }],
            'title': f'Price Trend for {area.title()}'
        }
 


