import os
import uuid
import random
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import your models and security
from app.models import (
    User, Organization, OrganizationMember, ScrapCategory, 
    ScrapListing, BuyerRequirement, MatchEvent,OTPRecord 
)
from app.models.user import UserRole
from app.models.organization import BusinessType, VerificationStatus
from app.models.organization_member import MemberRole
from app.models.scrap_listing import ListingStatus, ListingUnit
from app.models.buyer_requirement import RequirementStatus, RequirementUnit
from app.security import get_password_hash

# ⚠️ PASTE YOUR NEON DATABASE URL HERE ⚠️
# IMPORTANT: Change "postgresql://" to "postgresql+psycopg2://" at the start!
NEON_DB_URL = "postgresql://neondb_owner:npg_adsGt2cpf7mY@ep-crimson-salad-a15913c9-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

engine = create_engine(NEON_DB_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def clear_database():
    print("🗑️ Clearing old data...")
    db.query(OTPRecord).delete() 
    db.query(MatchEvent).delete()
    db.query(BuyerRequirement).delete()
    db.query(ScrapListing).delete()
    db.query(OrganizationMember).delete()
    db.query(Organization).delete()
    db.query(User).delete()
    db.commit()
    print("✅ Database cleared.")

def create_users_and_orgs():
    print("🏢 Creating 10 Users and Organizations...")
    password = get_password_hash("Password123")
    
    # 10 Organizations across India with real coordinates for the map
    orgs_data = [
        {"name": "Mumbai Metal Traders", "type": BusinessType.PROPRIETORSHIP, "city": "Mumbai", "state": "Maharashtra", "lat": 19.0760, "lng": 72.8777, "role": UserRole.SELLER},
        {"name": "Delhi Scrap Recycling", "type": BusinessType.COMPANY, "city": "Delhi", "state": "Delhi", "lat": 28.7041, "lng": 77.1025, "role": UserRole.SELLER},
        {"name": "Bangalore E-Waste Co", "type": BusinessType.PARTNERSHIP, "city": "Bangalore", "state": "Karnataka", "lat": 12.9716, "lng": 77.5946, "role": UserRole.SELLER},
        {"name": "Chennai Plastic Recyclers", "type": BusinessType.COMPANY, "city": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lng": 80.2707, "role": UserRole.SELLER},
        {"name": "Pune Iron & Steel", "type": BusinessType.PROPRIETORSHIP, "city": "Pune", "state": "Maharashtra", "lat": 18.5204, "lng": 73.8567, "role": UserRole.SELLER},
        {"name": "Ahmedabad Copper Works", "type": BusinessType.COMPANY, "city": "Ahmedabad", "state": "Gujarat", "lat": 23.0225, "lng": 72.5714, "role": UserRole.BUYER},
        {"name": "Kolkata Aluminum Corp", "type": BusinessType.COMPANY, "city": "Kolkata", "state": "West Bengal", "lat": 22.5726, "lng": 88.3639, "role": UserRole.BUYER},
        {"name": "Hyderabad Alloys", "type": BusinessType.PARTNERSHIP, "city": "Hyderabad", "state": "Telangana", "lat": 17.3850, "lng": 78.4867, "role": UserRole.BUYER},
        {"name": "Jaipur Brass Traders", "type": BusinessType.PROPRIETORSHIP, "city": "Jaipur", "state": "Rajasthan", "lat": 26.9124, "lng": 75.7873, "role": UserRole.BUYER},
        {"name": "Surat Textile Waste", "type": BusinessType.PARTNERSHIP, "city": "Surat", "state": "Gujarat", "lat": 21.1702, "lng": 72.8311, "role": UserRole.BUYER},
    ]
    
    users = []
    for i, data in enumerate(orgs_data):
        user = User(
            id=uuid.uuid4(),
            full_name=f"Manager {data['name']}",
            email=f"user{i+1}@scraplink.com",
            phone=f"+9198765432{i:02d}",
            password_hash=password,
            role=data["role"],
            email_verified=True,
            phone_verified=True
        )
        db.add(user)
        
        org = Organization(
            id=uuid.uuid4(),
            name=data["name"],
            business_type=data["type"],
            industry_type="Scrap & Recycling",
            location={"city": data["city"], "state": data["state"], "latitude": data["lat"], "longitude": data["lng"]},
            owner_user_id=user.id,
            verification_status=VerificationStatus.VERIFIED
        )
        db.add(org)
        db.flush() 

        member = OrganizationMember(
            id=uuid.uuid4(),
            organization_id=org.id,
            user_id=user.id,
            role=MemberRole.OWNER
        )
        db.add(member)
        users.append((user, org, data["role"]))
        
    db.commit()
    print("✅ Users and Organizations created.")
    return users

def create_listings_and_requirements(users):
    print("📦 Creating Listings and Requirements...")
    categories = {c.name: c.id for c in db.query(ScrapCategory).all()}
    sellers = [u for u in users if u[2] == UserRole.SELLER]
    buyers = [u for u in users if u[2] == UserRole.BUYER]
    
    # 15 Realistic Listings
    listings_data = [
        {"mat": "Copper Wire Scrap", "cat": "Copper", "qty": 500, "price": 720},
        {"mat": "Copper Tubing", "cat": "Copper", "qty": 300, "price": 680},
        {"mat": "Aluminum Extrusions", "cat": "Aluminium", "qty": 1200, "price": 180},
        {"mat": "Aluminum Cans (UBC)", "cat": "Aluminium", "qty": 2000, "price": 130},
        {"mat": "Steel HMS Scrap", "cat": "Steel", "qty": 5000, "price": 38},
        {"mat": "Stainless Steel 304", "cat": "Stainless Steel", "qty": 800, "price": 140},
        {"mat": "E-Waste PCBs", "cat": "Electronic Waste", "qty": 300, "price": 250},
        {"mat": "Brass Radiators", "cat": "Brass", "qty": 800, "price": 420},
        {"mat": "PET Bottles (Clear)", "cat": "Plastic - PET", "qty": 1000, "price": 45},
        {"mat": "HDPE Containers", "cat": "Plastic - HDPE", "qty": 1500, "price": 55},
        {"mat": "Lead Batteries", "cat": "Batteries", "qty": 2500, "price": 85},
        {"mat": "Zinc Die-Cast", "cat": "Zinc", "qty": 600, "price": 210},
        {"mat": "Copper Cables", "cat": "Cables & Wires", "qty": 400, "price": 450},
        {"mat": "Cast Iron Scrap", "cat": "Cast Iron", "qty": 3000, "price": 32},
        {"mat": "Mixed Paper Waste", "cat": "Paper & Cardboard", "qty": 5000, "price": 12}
    ]
    
    for i, l in enumerate(listings_data):
        seller_user, seller_org, _ = sellers[i % len(sellers)]
        
        # Skip if category isn't in DB to prevent crash
        if l["cat"] not in categories:
            continue
            
        listing = ScrapListing(
            id=uuid.uuid4(),
            seller_org_id=seller_org.id,
            category_id=categories[l["cat"]],
            material_name=l["mat"],
            quantity=Decimal(str(l["qty"])),
            unit=ListingUnit.KG,
            asking_price=Decimal(str(l["price"])),
            location=seller_org.location,
            availability_status=ListingStatus.ACTIVE,
            description=f"High grade {l['mat']} available. Ready for inspection and immediate dispatch from {seller_org.location['city']}."
        )
        db.add(listing)

    # 5 Buyer Requirements (for the Matchmaker)
    reqs_data = [
        {"mat": "Copper Wire Scrap", "cat": "Copper", "qty": 400, "desc": "Need clean copper wire, no insulation."},
        {"mat": "Steel Scrap", "cat": "Steel", "qty": 3000, "desc": "Looking for HMS steel scrap."},
        {"mat": "Aluminum Extrusions", "cat": "Aluminium", "qty": 1000, "desc": "6063 grade aluminum required."},
        {"mat": "Brass Scrap", "cat": "Brass", "qty": 500, "desc": "Yellow brass radiators."},
        {"mat": "PET Bottles", "cat": "Plastic - PET", "qty": 2000, "desc": "Clear PET bottles, baled."}
    ]
    
    for i, r in enumerate(reqs_data):
        buyer_user, buyer_org, _ = buyers[i % len(buyers)]
        
        if r["cat"] not in categories:
            continue
            
        req = BuyerRequirement(
            id=uuid.uuid4(),
            buyer_org_id=buyer_org.id,
            category_id=categories[r["cat"]],
            material_name=r["mat"],
            quantity=Decimal(str(r["qty"])),
            unit=RequirementUnit.KG,
            status=RequirementStatus.OPEN,
            description=r["desc"]
        )
        db.add(req)

        db.flush() # Flush to make sure reqs and listings have IDs

        print("🤝 Generating Dummy Match Alerts...")
        
        # Fetch the requirements and listings we just made
        all_reqs = db.query(BuyerRequirement).all()
        all_listings = db.query(ScrapListing).all()

        # Randomly match them
        for req in all_reqs:
            # Give each requirement 2-3 matches
            num_matches = random.randint(2, 3)
            matched_listings = random.sample(all_listings, num_matches)
            
            for listing in matched_listings:
                match = MatchEvent(
                    id=uuid.uuid4(),
                    requirement_id=req.id,
                    listing_id=listing.id,
                    similarity_score=Decimal(str(round(random.uniform(0.65, 0.95), 2))),
                    match_quality="EXCELLENT_MATCH" if random.uniform(0.8, 1.0) > 0.8 else "GOOD_MATCH"
                )
                db.add(match)
    db.commit()
    print("✅ Listings and Requirements created.")

if __name__ == "__main__":
    print("🚀 Starting Demo Data Seeding...")
    clear_database()
    users = create_users_and_orgs()
    create_listings_and_requirements(users)
    print("\n🎉 SUCCESS! Your Neon database is now full of demo data.")
    print("🔑 Password for ALL users: Password123")
    print("📧 Sellers: user1@scraplink.com to user5@scraplink.com")
    print("📧 Buyers:  user6@scraplink.com to user10@scraplink.com")