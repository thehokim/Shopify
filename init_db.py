"""
Database initialization script
Creates sample data for testing
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import (
    User, UserRole, Tenant, TenantStatus, Template,
    Category, Product, ProductStatus, ProductImage,
    ProductAttribute, ProductAttributeValue
)
from app.auth import get_password_hash


def init_db():
    """Initialize database with sample data"""
    
    print("🗄️  Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("👤 Creating super admin...")
        # Create super admin
        super_admin = User(
            email="admin@shopify.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Super Admin",
            role=UserRole.SUPER_ADMIN,
            is_active=True,
            is_verified=True
        )
        db.add(super_admin)
        db.flush()
        
        print("🎨 Creating templates...")
        # Create templates
        template1 = Template(
            name="Modern Fashion",
            description="Modern and clean template for fashion stores",
            preview_url="https://example.com/templates/modern-fashion.jpg",
            config={"primary_color": "#000000", "secondary_color": "#FFFFFF"}
        )
        db.add(template1)
        db.flush()
        
        print("🏪 Creating sample tenant...")
        # Create tenant owner
        owner = User(
            email="owner@fashionstore.com",
            hashed_password=get_password_hash("owner123"),
            full_name="Fashion Store Owner",
            role=UserRole.TENANT_OWNER,
            is_active=True
        )
        db.add(owner)
        db.flush()
        
        # Create tenant
        tenant = Tenant(
            name="Fashion Store",
            slug="fashion-store",
            domain="fashion-store.yourplatform.com",
            description="Your one-stop shop for fashion",
            owner_id=owner.id,
            template_id=template1.id,
            status=TenantStatus.ACTIVE
        )
        db.add(tenant)
        db.flush()
        
        # Update owner's tenant_id
        owner.tenant_id = tenant.id
        
        print("📦 Creating categories...")
        # Create categories
        clothing = Category(
            tenant_id=tenant.id,
            name="Clothing",
            slug="clothing",
            description="All clothing items",
            category_type="clothing",
            is_active=True
        )
        db.add(clothing)
        db.flush()
        
        tshirts = Category(
            tenant_id=tenant.id,
            name="T-Shirts",
            slug="t-shirts",
            parent_id=clothing.id,
            category_type="clothing",
            is_active=True
        )
        db.add(tshirts)
        db.flush()
        
        print("🏷️  Creating product attributes...")
        # Create attributes for clothing
        size_attr = ProductAttribute(
            category_id=clothing.id,
            name="Size",
            attribute_type="select",
            options=["XS", "S", "M", "L", "XL", "XXL"],
            is_required=True,
            is_variant=True,
            sort_order=1
        )
        db.add(size_attr)
        
        color_attr = ProductAttribute(
            category_id=clothing.id,
            name="Color",
            attribute_type="select",
            options=["Black", "White", "Red", "Blue", "Green"],
            is_required=True,
            is_variant=True,
            sort_order=2
        )
        db.add(color_attr)
        
        material_attr = ProductAttribute(
            category_id=clothing.id,
            name="Material",
            attribute_type="select",
            options=["100% Cotton", "Polyester", "Cotton Blend"],
            is_required=False,
            sort_order=3
        )
        db.add(material_attr)
        
        db.flush()
        
        print("👕 Creating sample products...")
        # Create sample products
        product1 = Product(
            tenant_id=tenant.id,
            category_id=tshirts.id,
            name="Black T-Shirt",
            slug="black-t-shirt",
            description="Classic cotton t-shirt with premium fit and comfort. Essential wardrobe piece for everyday wear.",
            short_description="Classic cotton t-shirt",
            sku="TSH-BLK-001",
            base_price=35.00,
            discount_price=25.00,
            cost_price=15.00,
            stock_quantity=100,
            status=ProductStatus.ACTIVE,
            is_featured=True
        )
        db.add(product1)
        db.flush()
        
        # Add product images
        image1 = ProductImage(
            product_id=product1.id,
            image_url="https://via.placeholder.com/800x800/000000/FFFFFF?text=Black+T-Shirt",
            alt_text="Black T-Shirt Front View",
            is_primary=True,
            sort_order=0
        )
        db.add(image1)
        
        # Add attribute values
        attr_val1 = ProductAttributeValue(
            product_id=product1.id,
            attribute_id=material_attr.id,
            value="100% Cotton"
        )
        db.add(attr_val1)
        
        # Product 2
        product2 = Product(
            tenant_id=tenant.id,
            category_id=tshirts.id,
            name="White T-Shirt",
            slug="white-t-shirt",
            description="Crisp white t-shirt made from premium cotton. Perfect for any occasion.",
            short_description="Premium white t-shirt",
            sku="TSH-WHT-001",
            base_price=30.00,
            stock_quantity=150,
            status=ProductStatus.ACTIVE,
            is_featured=True
        )
        db.add(product2)
        db.flush()
        
        image2 = ProductImage(
            product_id=product2.id,
            image_url="https://via.placeholder.com/800x800/FFFFFF/000000?text=White+T-Shirt",
            alt_text="White T-Shirt Front View",
            is_primary=True,
            sort_order=0
        )
        db.add(image2)
        
        # Product 3
        product3 = Product(
            tenant_id=tenant.id,
            category_id=tshirts.id,
            name="Red T-Shirt",
            slug="red-t-shirt",
            description="Bold red t-shirt that stands out. Comfortable and stylish.",
            short_description="Bold red t-shirt",
            sku="TSH-RED-001",
            base_price=32.00,
            discount_price=28.00,
            stock_quantity=80,
            status=ProductStatus.ACTIVE
        )
        db.add(product3)
        db.flush()
        
        image3 = ProductImage(
            product_id=product3.id,
            image_url="https://via.placeholder.com/800x800/FF0000/FFFFFF?text=Red+T-Shirt",
            alt_text="Red T-Shirt Front View",
            is_primary=True,
            sort_order=0
        )
        db.add(image3)
        
        print("👤 Creating sample customer...")
        # Create sample customer
        customer = User(
            email="customer@example.com",
            hashed_password=get_password_hash("customer123"),
            full_name="John Doe",
            phone="+998901234567",
            role=UserRole.CUSTOMER,
            is_active=True,
            tenant_id=tenant.id
        )
        db.add(customer)
        
        db.commit()
        
        print("✅ Database initialized successfully!")
        print("\n📋 Sample Credentials:")
        print("=" * 50)
        print("Super Admin:")
        print("  Email: admin@shopify.com")
        print("  Password: admin123")
        print("\nTenant Owner:")
        print("  Email: owner@fashionstore.com")
        print("  Password: owner123")
        print("\nCustomer:")
        print("  Email: customer@example.com")
        print("  Password: customer123")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
