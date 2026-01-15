"""
Create 4 sample products with full details (features, attributes, variants, etc.)
"""
import sys
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.product import (
    Product, ProductTranslation, ProductFeature, ProductFeatureTranslation,
    ProductAttribute, ProductAttributeTranslation, ProductVariantAttribute,
    ProductVariantAttributeTranslation, ProductType, ProductCondition, StockStatus
)
from app.models.product_variant import ProductVariant, StockStatus as VariantStockStatus
from app.models.brand import Brand
from app.models.tax_class import TaxClass
from app.models.category import Category
from datetime import datetime


def create_brands(db: Session):
    """Create or get brands"""
    brands = {}
    
    # Haier
    haier = db.query(Brand).filter(Brand.name == "Haier").first()
    if not haier:
        haier = Brand(name="Haier", image="https://example.com/brands/haier.png")
        db.add(haier)
        db.flush()
    brands['haier'] = haier
    
    # LG
    lg = db.query(Brand).filter(Brand.name == "LG").first()
    if not lg:
        lg = Brand(name="LG", image="https://example.com/brands/lg.png")
        db.add(lg)
        db.flush()
    brands['lg'] = lg
    
    # Samsung
    samsung = db.query(Brand).filter(Brand.name == "Samsung").first()
    if not samsung:
        samsung = Brand(name="Samsung", image="https://example.com/brands/samsung.png")
        db.add(samsung)
        db.flush()
    brands['samsung'] = samsung
    
    return brands


def get_tax_class(db: Session):
    """Get standard tax class"""
    tax = db.query(TaxClass).filter(TaxClass.name.like("%22%")).first()
    if not tax:
        tax = db.query(TaxClass).first()
    return tax


def create_product_1_haier_ac(db: Session, brands: dict, tax: TaxClass):
    """Product 1: Haier Smart Cool Air Conditioner"""
    print("Creating Product 1: Haier Air Conditioner...")
    
    product = Product(
        reference="HAIER-AC-9000",
        ean="8056379834721",
        product_type="configurable",
        is_active=True,
        price_list=599.00,
        currency="EUR",
        stock_status="in_stock",
        stock_quantity=15,
        condition="new",
        brand_id=brands['haier'].id,
        tax_class_id=tax.id,
        tax_included_in_price=False,
        date_add=datetime.now()
    )
    db.add(product)
    db.flush()
    
    # Translation
    translation = ProductTranslation(
        product_id=product.id,
        lang="it",
        title="Haier Smart Cool Condizionatore a Parete",
        sub_title="Climatizzatore Inverter 9000 BTU",
        simple_description="Condizionatore d'aria Haier Smart Cool con tecnologia inverter avanzata per un raffreddamento efficiente. Dotato di funzione Wi-Fi per controllo remoto tramite smartphone, modalità sleep silenziosa e filtro autopulente. Classe energetica A+++, ideale per ambienti fino a 25 mq. Design moderno e compatto che si adatta perfettamente a qualsiasi ambiente.",
        meta_description="Condizionatore Haier Smart Cool 9000 BTU Inverter WiFi A+++"
    )
    db.add(translation)
    
    # Features
    features_data = [
        ("Potenza di raffreddamento", "9000 BTU/h"),
        ("Classe energetica", "A+++"),
        ("Tecnologia", "Inverter"),
        ("Livello rumore interno", "22 dB"),
        ("Superficie consigliata", "Fino a 25 mq"),
        ("Funzioni speciali", "Wi-Fi, Modalità Sleep, Autopulente"),
        ("Dimensioni unità interna", "79 x 29 x 21 cm"),
        ("Peso", "9 kg"),
        ("Gas refrigerante", "R32"),
        ("Consumo annuo", "165 kWh/anno")
    ]
    
    for idx, (name, value) in enumerate(features_data, 1):
        feature = ProductFeature(product_id=product.id, code=f"ac_feature_{idx}")
        db.add(feature)
        db.flush()
        
        feat_trans = ProductFeatureTranslation(
            feature_id=feature.id,
            lang="it",
            name=name,
            value=value
        )
        db.add(feat_trans)
    
    # Attributes
    attributes_data = [
        ("color", "Colore", "Bianco"),
        ("warranty", "Garanzia", "2 anni"),
        ("origin", "Paese d'origine", "Cina"),
        ("installation", "Installazione", "Richiesta installazione professionale")
    ]
    
    for code, name, value in attributes_data:
        attribute = ProductAttribute(product_id=product.id, code=code)
        db.add(attribute)
        db.flush()
        
        attr_trans = ProductAttributeTranslation(
            attribute_id=attribute.id,
            lang="it",
            name=name,
            value=value
        )
        db.add(attr_trans)
    
    # Variant Attributes (BTU capacity options)
    var_attr = ProductVariantAttribute(product_id=product.id, code="btu_capacity")
    db.add(var_attr)
    db.flush()
    
    var_attr_trans = ProductVariantAttributeTranslation(
        variant_attribute_id=var_attr.id,
        lang="it",
        label="Capacità BTU"
    )
    db.add(var_attr_trans)
    
    # Variants (different BTU capacities)
    variants_data = [
        ("HAIER-AC-9000-V1", "9000 BTU", 599.00, 15),
        ("HAIER-AC-12000-V2", "12000 BTU", 749.00, 10),
        ("HAIER-AC-18000-V3", "18000 BTU", 949.00, 8)
    ]
    
    for ref, btu, price, stock in variants_data:
        variant = ProductVariant(
            parent_product_id=product.id,
            reference=ref,
            ean=f"805637983{ref[-1]}999",
            is_active=True,
            price_list=price,
            currency="EUR",
            stock_status="in_stock",
            stock_quantity=stock,
            attributes={"btu_capacity": btu}
        )
        db.add(variant)
    
    print(f"✓ Product 1 created with ID: {product.id}")
    return product.id


def create_product_2_lg_washer(db: Session, brands: dict, tax: TaxClass):
    """Product 2: LG Front Load Washing Machine"""
    print("Creating Product 2: LG Washing Machine...")
    
    product = Product(
        reference="LG-WM-F4V5VYP2T",
        ean="8806098671298",
        product_type="configurable",
        is_active=True,
        price_list=449.00,
        currency="EUR",
        stock_status="in_stock",
        stock_quantity=20,
        condition="new",
        brand_id=brands['lg'].id,
        tax_class_id=tax.id,
        tax_included_in_price=False,
        date_add=datetime.now()
    )
    db.add(product)
    db.flush()
    
    # Translation
    translation = ProductTranslation(
        product_id=product.id,
        lang="it",
        title="Lavatrice LG Carica Frontale 9 kg",
        sub_title="Lavatrice con Intelligenza Artificiale AI DD",
        simple_description="Lavatrice LG a carica frontale da 9 kg con tecnologia AI Direct Drive che rileva automaticamente il peso e il tessuto per ottimizzare i movimenti del cestello. Dotata di funzione Steam per igienizzare i capi, motore Inverter Direct Drive silenzioso e affidabile con garanzia 10 anni. Classe energetica A, 1400 giri/min, display LED e connettività Wi-Fi per controllo da smartphone tramite app ThinQ.",
        meta_description="Lavatrice LG 9kg AI Direct Drive Steam WiFi A 1400rpm"
    )
    db.add(translation)
    
    # Features
    features_data = [
        ("Capacità di carico", "9 kg"),
        ("Classe energetica", "A"),
        ("Velocità centrifuga", "1400 giri/min"),
        ("Tecnologia lavaggio", "AI Direct Drive"),
        ("Livello rumore lavaggio", "52 dB"),
        ("Livello rumore centrifuga", "74 dB"),
        ("Programmi speciali", "Steam, Allergy Care, Quick Wash 30min"),
        ("Dimensioni (L x P x A)", "60 x 56 x 85 cm"),
        ("Peso", "66 kg"),
        ("Connettività", "Wi-Fi - App ThinQ"),
        ("Consumo acqua annuo", "9500 litri/anno"),
        ("Garanzia motore", "10 anni")
    ]
    
    for idx, (name, value) in enumerate(features_data, 1):
        feature = ProductFeature(product_id=product.id, code=f"washer_feature_{idx}")
        db.add(feature)
        db.flush()
        
        feat_trans = ProductFeatureTranslation(
            feature_id=feature.id,
            lang="it",
            name=name,
            value=value
        )
        db.add(feat_trans)
    
    # Attributes
    attributes_data = [
        ("color", "Colore", "Bianco"),
        ("door_type", "Tipo porta", "Carica frontale"),
        ("warranty", "Garanzia", "2 anni + 10 anni motore"),
        ("origin", "Paese d'origine", "Corea del Sud")
    ]
    
    for code, name, value in attributes_data:
        attribute = ProductAttribute(product_id=product.id, code=code)
        db.add(attribute)
        db.flush()
        
        attr_trans = ProductAttributeTranslation(
            attribute_id=attribute.id,
            lang="it",
            name=name,
            value=value
        )
        db.add(attr_trans)
    
    # Variant Attributes (capacity options)
    var_attr = ProductVariantAttribute(product_id=product.id, code="capacity")
    db.add(var_attr)
    db.flush()
    
    var_attr_trans = ProductVariantAttributeTranslation(
        variant_attribute_id=var_attr.id,
        lang="it",
        label="Capacità"
    )
    db.add(var_attr_trans)
    
    # Variants
    variants_data = [
        ("LG-WM-7KG", "7 kg", 389.00, 25),
        ("LG-WM-9KG", "9 kg", 449.00, 20),
        ("LG-WM-11KG", "11 kg", 549.00, 12)
    ]
    
    for ref, capacity, price, stock in variants_data:
        variant = ProductVariant(
            parent_product_id=product.id,
            reference=ref,
            ean=f"880609867{ref[-3]}298",
            is_active=True,
            price_list=price,
            currency="EUR",
            stock_status="in_stock",
            stock_quantity=stock,
            attributes={"capacity": capacity}
        )
        db.add(variant)
    
    print(f"✓ Product 2 created with ID: {product.id}")
    return product.id


def create_product_3_samsung_tv(db: Session, brands: dict, tax: TaxClass):
    """Product 3: Samsung 55" TV"""
    print("Creating Product 3: Samsung TV...")
    
    product = Product(
        reference="SAMSUNG-TV-UE55CU7090",
        ean="8806094936766",
        product_type="configurable",
        is_active=True,
        price_list=499.00,
        currency="EUR",
        stock_status="in_stock",
        stock_quantity=18,
        condition="new",
        brand_id=brands['samsung'].id,
        tax_class_id=tax.id,
        tax_included_in_price=False,
        date_add=datetime.now()
    )
    db.add(product)
    db.flush()
    
    # Translation
    translation = ProductTranslation(
        product_id=product.id,
        lang="it",
        title="TV Samsung 55 Pollici Crystal UHD 4K",
        sub_title="Smart TV con Crystal Processor 4K e Tizen OS",
        simple_description="Smart TV Samsung da 55 pollici con risoluzione Crystal UHD 4K per immagini nitide e dettagliate. Dotato di processore Crystal Processor 4K che ottimizza automaticamente colori e contrasto. Sistema operativo Tizen con accesso a tutte le app di streaming (Netflix, Prime Video, Disney+). Supporto HDR10+, modalità Gaming con input lag ridotto, AirPlay 2 e SmartThings. Audio Dolby Digital Plus con tecnologia Adaptive Sound che si adatta ai contenuti.",
        meta_description="TV Samsung 55'' Crystal UHD 4K Smart TV HDR10+ Tizen"
    )
    db.add(translation)
    
    # Features
    features_data = [
        ("Dimensione schermo", "55 pollici (138 cm)"),
        ("Risoluzione", "3840 x 2160 (4K UHD)"),
        ("Tipo pannello", "Crystal UHD LED"),
        ("Processore", "Crystal Processor 4K"),
        ("HDR", "HDR10+"),
        ("Frequenza aggiornamento", "50 Hz"),
        ("Sistema operativo", "Tizen OS"),
        ("Connettività", "WiFi 5, Bluetooth 5.2, Ethernet"),
        ("Porte HDMI", "3 porte HDMI 2.0"),
        ("Porte USB", "2 porte USB 2.0"),
        ("Audio", "Dolby Digital Plus, 20W (2 canali)"),
        ("Dimensioni con base", "123 x 78 x 25 cm"),
        ("Peso", "13.5 kg"),
        ("Consumo energetico", "Classe G (83 kWh/1000h)")
    ]
    
    for idx, (name, value) in enumerate(features_data, 1):
        feature = ProductFeature(product_id=product.id, code=f"tv_feature_{idx}")
        db.add(feature)
        db.flush()
        
        feat_trans = ProductFeatureTranslation(
            feature_id=feature.id,
            lang="it",
            name=name,
            value=value
        )
        db.add(feat_trans)
    
    # Attributes
    attributes_data = [
        ("color", "Colore", "Nero"),
        ("smart_tv", "Smart TV", "Sì - Tizen OS"),
        ("warranty", "Garanzia", "2 anni"),
        ("origin", "Paese d'origine", "Corea del Sud"),
        ("vesa", "Supporto VESA", "200 x 200 mm")
    ]
    
    for code, name, value in attributes_data:
        attribute = ProductAttribute(product_id=product.id, code=code)
        db.add(attribute)
        db.flush()
        
        attr_trans = ProductAttributeTranslation(
            attribute_id=attribute.id,
            lang="it",
            name=name,
            value=value
        )
        db.add(attr_trans)
    
    # Variant Attributes (screen size)
    var_attr = ProductVariantAttribute(product_id=product.id, code="screen_size")
    db.add(var_attr)
    db.flush()
    
    var_attr_trans = ProductVariantAttributeTranslation(
        variant_attribute_id=var_attr.id,
        lang="it",
        label="Dimensione Schermo"
    )
    db.add(var_attr_trans)
    
    # Variants
    variants_data = [
        ("SAMSUNG-TV-43", "43 pollici", 349.00, 22),
        ("SAMSUNG-TV-55", "55 pollici", 499.00, 18),
        ("SAMSUNG-TV-65", "65 pollici", 699.00, 10),
        ("SAMSUNG-TV-75", "75 pollici", 949.00, 5)
    ]
    
    for ref, size, price, stock in variants_data:
        variant = ProductVariant(
            parent_product_id=product.id,
            reference=ref,
            ean=f"880609493{ref[-2:]}66",
            is_active=True,
            price_list=price,
            currency="EUR",
            stock_status="in_stock" if stock > 0 else "low_stock",
            stock_quantity=stock,
            attributes={"screen_size": size}
        )
        db.add(variant)
    
    print(f"✓ Product 3 created with ID: {product.id}")
    return product.id


def create_product_4_haier_fridge(db: Session, brands: dict, tax: TaxClass):
    """Product 4: Haier Refrigerator 2 Doors"""
    print("Creating Product 4: Haier Refrigerator...")
    
    product = Product(
        reference="HAIER-FRIDGE-HTR3619FNMP",
        ean="6901018167234",
        product_type="configurable",
        is_active=True,
        price_list=599.00,
        currency="EUR",
        stock_status="in_stock",
        stock_quantity=12,
        condition="new",
        brand_id=brands['haier'].id,
        tax_class_id=tax.id,
        tax_included_in_price=False,
        date_add=datetime.now()
    )
    db.add(product)
    db.flush()
    
    # Translation
    translation = ProductTranslation(
        product_id=product.id,
        lang="it",
        title="Haier Frigorifero 2 Porte 357 Litri",
        sub_title="Frigorifero No Frost con Fresh Zone 0°C",
        simple_description="Frigorifero combinato Haier da 357 litri con tecnologia Total No Frost che previene la formazione di ghiaccio. Dotato di zona Fresh Zone 0°C per conservare più a lungo carne e pesce, ripiani in vetro temperato regolabili, cassetti frutta e verdura ad alta umidità. Classe energetica F, sistema Multi Air Flow per distribuzione uniforme del freddo, display LED touch control esterno, illuminazione interna LED. Design elegante in acciaio inox antimpronta con maniglie integrate.",
        meta_description="Frigorifero Haier 357L No Frost Fresh Zone 0°C Inox"
    )
    db.add(translation)
    
    # Features
    features_data = [
        ("Capacità totale", "357 litri"),
        ("Capacità frigo", "250 litri"),
        ("Capacità freezer", "107 litri"),
        ("Classe energetica", "F"),
        ("Tecnologia", "Total No Frost"),
        ("Zona speciale", "Fresh Zone 0°C"),
        ("Livello rumore", "39 dB"),
        ("Sistema raffreddamento", "Multi Air Flow"),
        ("Ripiani frigo", "4 ripiani in vetro temperato"),
        ("Cassetti freezer", "3 cassetti trasparenti"),
        ("Illuminazione", "LED"),
        ("Display", "Touch control LED esterno"),
        ("Dimensioni (L x P x A)", "70 x 67 x 190 cm"),
        ("Peso", "78 kg"),
        ("Consumo energetico", "278 kWh/anno")
    ]
    
    for idx, (name, value) in enumerate(features_data, 1):
        feature = ProductFeature(product_id=product.id, code=f"fridge_feature_{idx}")
        db.add(feature)
        db.flush()
        
        feat_trans = ProductFeatureTranslation(
            feature_id=feature.id,
            lang="it",
            name=name,
            value=value
        )
        db.add(feat_trans)
    
    # Attributes
    attributes_data = [
        ("color", "Colore", "Inox"),
        ("door_type", "Tipo porte", "2 porte (frigo sopra, freezer sotto)"),
        ("warranty", "Garanzia", "2 anni"),
        ("origin", "Paese d'origine", "Cina"),
        ("reversible_door", "Porta reversibile", "Sì")
    ]
    
    for code, name, value in attributes_data:
        attribute = ProductAttribute(product_id=product.id, code=code)
        db.add(attribute)
        db.flush()
        
        attr_trans = ProductAttributeTranslation(
            attribute_id=attribute.id,
            lang="it",
            name=name,
            value=value
        )
        db.add(attr_trans)
    
    # Variant Attributes (capacity and color)
    var_attr_capacity = ProductVariantAttribute(product_id=product.id, code="capacity")
    db.add(var_attr_capacity)
    db.flush()
    
    var_attr_capacity_trans = ProductVariantAttributeTranslation(
        variant_attribute_id=var_attr_capacity.id,
        lang="it",
        label="Capacità"
    )
    db.add(var_attr_capacity_trans)
    
    var_attr_color = ProductVariantAttribute(product_id=product.id, code="color")
    db.add(var_attr_color)
    db.flush()
    
    var_attr_color_trans = ProductVariantAttributeTranslation(
        variant_attribute_id=var_attr_color.id,
        lang="it",
        label="Colore"
    )
    db.add(var_attr_color_trans)
    
    # Variants
    variants_data = [
        ("HAIER-FRIDGE-357-INOX", "357 litri", "Inox", 599.00, 12, "6901018167001"),
        ("HAIER-FRIDGE-357-WHITE", "357 litri", "Bianco", 579.00, 15, "6901018167002"),
        ("HAIER-FRIDGE-420-INOX", "420 litri", "Inox", 749.00, 8, "6901018167003"),
        ("HAIER-FRIDGE-420-WHITE", "420 litri", "Bianco", 729.00, 10, "6901018167004")
    ]
    
    for ref, capacity, color, price, stock, ean in variants_data:
        variant = ProductVariant(
            parent_product_id=product.id,
            reference=ref,
            ean=ean,
            is_active=True,
            price_list=price,
            currency="EUR",
            stock_status="in_stock",
            stock_quantity=stock,
            attributes={"capacity": capacity, "color": color}
        )
        db.add(variant)
    
    print(f"✓ Product 4 created with ID: {product.id}")
    return product.id


def link_related_products(db: Session, product_ids: dict):
    """Link products as related"""
    print("\nLinking related products...")
    
    # AC related to Fridge (both Haier)
    ac_product = db.query(Product).filter(Product.id == product_ids['ac']).first()
    fridge_product = db.query(Product).filter(Product.id == product_ids['fridge']).first()
    if ac_product and fridge_product:
        ac_product.related_products.append(fridge_product)
        fridge_product.related_products.append(ac_product)
    
    # Washer related to TV (electronics)
    washer_product = db.query(Product).filter(Product.id == product_ids['washer']).first()
    tv_product = db.query(Product).filter(Product.id == product_ids['tv']).first()
    if washer_product and tv_product:
        washer_product.related_products.append(tv_product)
        tv_product.related_products.append(washer_product)
    
    # Fridge related to Washer (large appliances)
    if fridge_product and washer_product:
        fridge_product.related_products.append(washer_product)
        washer_product.related_products.append(fridge_product)
    
    print("✓ Related products linked")


def main():
    print("="*60)
    print("Creating 4 Sample Products with Full Details")
    print("="*60)
    
    db = SessionLocal()
    try:
        # Create brands
        brands = create_brands(db)
        
        # Get tax class
        tax = get_tax_class(db)
        if not tax:
            print("❌ Error: No tax class found in database")
            return
        
        # Create products
        product_ids = {}
        product_ids['ac'] = create_product_1_haier_ac(db, brands, tax)
        product_ids['washer'] = create_product_2_lg_washer(db, brands, tax)
        product_ids['tv'] = create_product_3_samsung_tv(db, brands, tax)
        product_ids['fridge'] = create_product_4_haier_fridge(db, brands, tax)
        
        # Link related products
        link_related_products(db, product_ids)
        
        # Commit all changes
        db.commit()
        
        print("\n" + "="*60)
        print("✓ All 4 products created successfully!")
        print("="*60)
        print("\nProduct IDs:")
        print(f"1. Haier Air Conditioner: {product_ids['ac']}")
        print(f"2. LG Washing Machine: {product_ids['washer']}")
        print(f"3. Samsung TV: {product_ids['tv']}")
        print(f"4. Haier Refrigerator: {product_ids['fridge']}")
        print("\nYou can now access these products via API:")
        print(f"GET /api/v1/products/{product_ids['ac']}")
        print(f"GET /api/v1/products/{product_ids['washer']}")
        print(f"GET /api/v1/products/{product_ids['tv']}")
        print(f"GET /api/v1/products/{product_ids['fridge']}")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
