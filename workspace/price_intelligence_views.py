"""
Price Intelligence System Views
Material pricing data, scraping, and market analysis
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg, Min, Max
from datetime import datetime, timedelta
import requests
import json

# BeautifulSoup import - install with: pip install beautifulsoup4
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

from .models import PriceIntelligence, MaterialReference, Job
from .serializers import PriceIntelligenceSerializer, MaterialReferenceSerializer
from authentication.permissions import IsAdmin, IsAdminOrFM


# ==================== Price Intelligence Management ====================

class PriceIntelligenceListView(generics.ListAPIView):
    """List price intelligence data"""
    serializer_class = PriceIntelligenceSerializer
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def get_queryset(self):
        queryset = PriceIntelligence.objects.all().order_by('-last_scraped')
        
        # Filter by material name
        material_name = self.request.query_params.get('material_name')
        if material_name:
            queryset = queryset.filter(material_name__icontains=material_name)
        
        # Filter by supplier
        supplier = self.request.query_params.get('supplier')
        if supplier:
            queryset = queryset.filter(supplier=supplier)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__icontains=category)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(current_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(current_price__lte=max_price)
        
        return queryset


class MaterialPriceComparisonView(APIView):
    """Compare prices across suppliers for a material"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def get(self, request):
        material_name = request.query_params.get('material_name')
        
        if not material_name:
            return Response(
                {'error': 'material_name parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all price data for this material
        price_data = PriceIntelligence.objects.filter(
            material_name__icontains=material_name
        ).order_by('current_price')
        
        if not price_data.exists():
            return Response(
                {'error': 'No price data found for this material'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Calculate statistics
        prices = [item.current_price for item in price_data]
        
        comparison = {
            'material_name': material_name,
            'total_suppliers': price_data.count(),
            'price_range': {
                'min': min(prices),
                'max': max(prices),
                'average': sum(prices) / len(prices)
            },
            'suppliers': PriceIntelligenceSerializer(price_data, many=True).data,
            'best_deal': PriceIntelligenceSerializer(price_data.first()).data,
            'last_updated': price_data.order_by('-last_scraped').first().last_scraped
        }
        
        return Response(comparison)


class MaterialSearchView(APIView):
    """Search materials across all suppliers"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def get(self, request):
        query = request.query_params.get('q')
        
        if not query:
            return Response(
                {'error': 'Search query (q) is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Search across material names and descriptions
        results = PriceIntelligence.objects.filter(
            Q(material_name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__icontains=query) |
            Q(category__icontains=query)
        ).order_by('current_price')[:50]
        
        # Group by material name for better presentation
        grouped_results = {}
        for item in results:
            material_key = item.material_name.lower()
            if material_key not in grouped_results:
                grouped_results[material_key] = {
                    'material_name': item.material_name,
                    'category': item.category,
                    'suppliers': []
                }
            
            grouped_results[material_key]['suppliers'].append({
                'supplier': item.supplier,
                'price': float(item.current_price),
                'brand': item.brand,
                'product_url': item.product_url,
                'in_stock': item.in_stock,
                'last_scraped': item.last_scraped
            })
        
        return Response({
            'query': query,
            'total_results': len(results),
            'materials': list(grouped_results.values())
        })


# ==================== Price Scraping System ====================

class TriggerPriceScrapingView(APIView):
    """Trigger price scraping for specific materials"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request):
        materials = request.data.get('materials', [])
        suppliers = request.data.get('suppliers', ['HOME_DEPOT', 'LOWES'])
        
        if not materials:
            return Response(
                {'error': 'Materials list is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        scraping_results = []
        
        for material in materials:
            for supplier in suppliers:
                try:
                    result = self._scrape_material_price(material, supplier)
                    scraping_results.append(result)
                except Exception as e:
                    scraping_results.append({
                        'material': material,
                        'supplier': supplier,
                        'status': 'error',
                        'error': str(e)
                    })
        
        return Response({
            'message': 'Price scraping completed',
            'results': scraping_results,
            'total_processed': len(scraping_results),
            'successful': len([r for r in scraping_results if r.get('status') == 'success'])
        })
    
    def _scrape_material_price(self, material_name, supplier):
        """Scrape price for a specific material from supplier"""
        # Mock implementation - replace with actual scraping logic
        
        if supplier == 'HOME_DEPOT':
            return self._scrape_home_depot(material_name)
        elif supplier == 'LOWES':
            return self._scrape_lowes(material_name)
        elif supplier == 'AMAZON':
            return self._scrape_amazon(material_name)
        else:
            raise ValueError(f"Unsupported supplier: {supplier}")
    
    def _scrape_home_depot(self, material_name):
        """Scrape Home Depot prices"""
        # Mock implementation
        mock_data = {
            'material_name': material_name,
            'supplier': 'HOME_DEPOT',
            'current_price': 29.99,
            'brand': 'Behr',
            'description': f'{material_name} - Premium Quality',
            'product_url': f'https://homedepot.com/search/{material_name.replace(" ", "+")}',
            'in_stock': True,
            'category': 'Paint & Supplies'
        }
        
        # Create or update price intelligence record
        price_intel, created = PriceIntelligence.objects.update_or_create(
            material_name=material_name,
            supplier='HOME_DEPOT',
            defaults=mock_data
        )
        
        return {
            'material': material_name,
            'supplier': 'HOME_DEPOT',
            'status': 'success',
            'price': mock_data['current_price'],
            'created': created
        }
    
    def _scrape_lowes(self, material_name):
        """Scrape Lowe's prices"""
        # Mock implementation
        mock_data = {
            'material_name': material_name,
            'supplier': 'LOWES',
            'current_price': 31.49,
            'brand': 'Valspar',
            'description': f'{material_name} - Professional Grade',
            'product_url': f'https://lowes.com/search?searchTerm={material_name.replace(" ", "+")}',
            'in_stock': True,
            'category': 'Paint & Supplies'
        }
        
        price_intel, created = PriceIntelligence.objects.update_or_create(
            material_name=material_name,
            supplier='LOWES',
            defaults=mock_data
        )
        
        return {
            'material': material_name,
            'supplier': 'LOWES',
            'status': 'success',
            'price': mock_data['current_price'],
            'created': created
        }
    
    def _scrape_amazon(self, material_name):
        """Scrape Amazon prices"""
        # Mock implementation
        mock_data = {
            'material_name': material_name,
            'supplier': 'AMAZON',
            'current_price': 27.99,
            'brand': 'Various',
            'description': f'{material_name} - Multiple Options Available',
            'product_url': f'https://amazon.com/s?k={material_name.replace(" ", "+")}',
            'in_stock': True,
            'category': 'Home Improvement'
        }
        
        price_intel, created = PriceIntelligence.objects.update_or_create(
            material_name=material_name,
            supplier='AMAZON',
            defaults=mock_data
        )
        
        return {
            'material': material_name,
            'supplier': 'AMAZON',
            'status': 'success',
            'price': mock_data['current_price'],
            'created': created
        }


class AutoScrapingScheduleView(APIView):
    """Schedule automatic price scraping"""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request):
        # This would integrate with Celery for scheduled tasks
        materials_to_scrape = [
            'Interior Paint - Gallon',
            'Exterior Paint - Gallon',
            'Paint Primer - Gallon',
            'Paint Brushes - Set',
            'Paint Rollers - Set',
            'Drop Cloths',
            'Painter\'s Tape',
            'Sandpaper - Assorted',
            'Wood Stain - Quart',
            'Polyurethane Finish - Quart'
        ]
        
        # Mock scheduling response
        return Response({
            'message': 'Automatic price scraping scheduled',
            'materials_count': len(materials_to_scrape),
            'schedule': 'Daily at 2:00 AM',
            'next_run': timezone.now() + timedelta(days=1)
        })


# ==================== Material References for Jobs ====================

class JobMaterialReferencesView(generics.ListCreateAPIView):
    """List and create material references for jobs"""
    serializer_class = MaterialReferenceSerializer
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        return MaterialReference.objects.filter(job_id=job_id).order_by('item_name')
    
    def perform_create(self, serializer):
        job_id = self.kwargs.get('job_id')
        job = get_object_or_404(Job, id=job_id)
        
        material_name = serializer.validated_data['item_name']
        
        # Try to get current pricing data
        price_data = PriceIntelligence.objects.filter(
            material_name__icontains=material_name
        ).order_by('current_price')
        
        if price_data.exists():
            # Use the best price as low, highest as high
            serializer.validated_data['price_low'] = price_data.first().current_price
            serializer.validated_data['price_high'] = price_data.last().current_price
            
            # Use the best deal's purchase URL
            best_deal = price_data.first()
            serializer.validated_data['purchase_url'] = best_deal.product_url
            serializer.validated_data['supplier'] = best_deal.get_supplier_display()
        
        serializer.save(job=job)


class MaterialReferenceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete material reference"""
    serializer_class = MaterialReferenceSerializer
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    queryset = MaterialReference.objects.all()


class UpdateMaterialPricingView(APIView):
    """Update material reference pricing from intelligence data"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def post(self, request, material_ref_id):
        material_ref = get_object_or_404(MaterialReference, id=material_ref_id)
        
        # Find matching price intelligence data
        price_data = PriceIntelligence.objects.filter(
            material_name__icontains=material_ref.item_name
        ).order_by('current_price')
        
        if not price_data.exists():
            return Response(
                {'error': 'No pricing data found for this material'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update pricing
        best_deal = price_data.first()
        highest_price = price_data.last()
        
        material_ref.price_low = best_deal.current_price
        material_ref.price_high = highest_price.current_price
        material_ref.purchase_url = best_deal.product_url
        material_ref.supplier = best_deal.get_supplier_display()
        material_ref.save()
        
        return Response({
            'message': 'Material pricing updated successfully',
            'material_reference': MaterialReferenceSerializer(material_ref).data,
            'price_sources': PriceIntelligenceSerializer(price_data, many=True).data
        })


# ==================== Price Analytics ====================

class PriceAnalyticsView(APIView):
    """Price analytics and trends"""
    permission_classes = [IsAuthenticated, IsAdminOrFM]
    
    def get(self, request):
        # Price trends over time
        recent_data = PriceIntelligence.objects.filter(
            last_scraped__gte=timezone.now() - timedelta(days=30)
        )
        
        # Supplier comparison
        supplier_stats = recent_data.values('supplier').annotate(
            avg_price=Avg('current_price'),
            min_price=Min('current_price'),
            max_price=Max('current_price'),
            product_count=Count('id')
        ).order_by('avg_price')
        
        # Category analysis
        category_stats = recent_data.values('category').annotate(
            avg_price=Avg('current_price'),
            product_count=Count('id')
        ).order_by('-avg_price')
        
        # Price change analysis
        price_changes = recent_data.exclude(previous_price__isnull=True)
        price_increases = price_changes.filter(current_price__gt=models.F('previous_price')).count()
        price_decreases = price_changes.filter(current_price__lt=models.F('previous_price')).count()
        
        return Response({
            'summary': {
                'total_products_tracked': recent_data.count(),
                'average_price': recent_data.aggregate(avg=Avg('current_price'))['avg'],
                'price_increases': price_increases,
                'price_decreases': price_decreases,
                'last_updated': recent_data.order_by('-last_scraped').first().last_scraped if recent_data.exists() else None
            },
            'supplier_comparison': list(supplier_stats),
            'category_analysis': list(category_stats)
        })