from elasticsearch import Elasticsearch
from typing import List, Dict, Any, Optional
from app.config import settings


class ElasticsearchService:
    def __init__(self):
        self.es = Elasticsearch([settings.ELASTICSEARCH_URL])
        # Не создаем индексы сразу - сделаем это при первом использовании
        self._indices_created = False
    
    def _ensure_indices(self):
        """Create indices if they don't exist"""
        if self._indices_created:
            return
            
        try:
            index_name = settings.ELASTICSEARCH_INDEX_PRODUCTS
            
            if not self.es.indices.exists(index=index_name):
                # Create index with mapping
                mapping = {
                    "mappings": {
                        "properties": {
                            "id": {"type": "integer"},
                            "tenant_id": {"type": "integer"},
                            "name": {
                                "type": "text",
                                "analyzer": "standard",
                                "fields": {
                                    "keyword": {"type": "keyword"}
                                }
                            },
                            "description": {"type": "text"},
                            "category_name": {"type": "keyword"},
                            "category_id": {"type": "integer"},
                            "base_price": {"type": "float"},
                            "discount_price": {"type": "float"},
                            "sku": {"type": "keyword"},
                            "status": {"type": "keyword"},
                            "is_featured": {"type": "boolean"},
                            "stock_quantity": {"type": "integer"},
                            "created_at": {"type": "date"},
                        }
                    }
                }
                self.es.indices.create(index=index_name, body=mapping)
            
            self._indices_created = True
        except Exception as e:
            print(f"Warning: Could not create Elasticsearch indices: {e}")
            print("Elasticsearch will be initialized on first use")
    
    def index_product(self, product_data: Dict[str, Any]) -> bool:
        """Index a product"""
        try:
            self._ensure_indices()  # Создаем индексы при первом использовании
            self.es.index(
                index=settings.ELASTICSEARCH_INDEX_PRODUCTS,
                id=product_data["id"],
                document=product_data
            )
            return True
        except Exception as e:
            print(f"Error indexing product: {e}")
            return False
    
    def search_products(
        self,
        tenant_id: int,
        query: str = "",
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "relevance"
    ) -> Dict[str, Any]:
        """Search products with filters"""
        try:
            self._ensure_indices()  # Создаем индексы при первом использовании
            
            # Build query
            must_clauses = [
                {"term": {"tenant_id": tenant_id}},
                {"term": {"status": "active"}}
            ]
            
            if query:
                must_clauses.append({
                    "multi_match": {
                        "query": query,
                        "fields": ["name^3", "description^2"],
                        "fuzziness": "AUTO"
                    }
                })
            
            # Build sort
            sort = []
            if sort_by == "price_asc":
                sort.append({"base_price": "asc"})
            elif sort_by == "price_desc":
                sort.append({"base_price": "desc"})
            elif sort_by == "newest":
                sort.append({"created_at": "desc"})
            else:
                if query:
                    sort.append("_score")
                else:
                    sort.append({"created_at": "desc"})
            
            # Execute search
            body = {
                "query": {
                    "bool": {
                        "must": must_clauses
                    }
                },
                "sort": sort,
                "from": (page - 1) * page_size,
                "size": page_size
            }
            
            response = self.es.search(
                index=settings.ELASTICSEARCH_INDEX_PRODUCTS,
                body=body
            )
            
            hits = response["hits"]
            return {
                "total": hits["total"]["value"],
                "page": page,
                "page_size": page_size,
                "products": [hit["_source"] for hit in hits["hits"]]
            }
        
        except Exception as e:
            print(f"Error searching products: {e}")
            return {
                "total": 0,
                "page": page,
                "page_size": page_size,
                "products": []
            }
    
    def delete_product(self, product_id: int) -> bool:
        """Delete a product from index"""
        try:
            self.es.delete(
                index=settings.ELASTICSEARCH_INDEX_PRODUCTS,
                id=product_id
            )
            return True
        except Exception as e:
            print(f"Error deleting product: {e}")
            return False


# Create singleton instance
es_service = ElasticsearchService()