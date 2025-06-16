#!/bin/bash

# API Key Manager Setup Script

echo "🔐 API Key Manager Setup"
echo "========================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    
    # Generate random secrets
    SESSION_SECRET=$(openssl rand -base64 32)
    JWT_SECRET=$(openssl rand -base64 32)
    ENCRYPTION_KEY=$(openssl rand -base64 24 | head -c 32)
    
    # Update .env file with generated secrets
    sed -i "s/SESSION_SECRET=.*/SESSION_SECRET=$SESSION_SECRET/" .env
    sed -i "s/JWT_SECRET=.*/JWT_SECRET=$JWT_SECRET/" .env
    sed -i "s/ENCRYPTION_KEY=.*/ENCRYPTION_KEY=$ENCRYPTION_KEY/" .env
    
    echo "✅ Generated secure secrets"
    echo ""
    echo "⚠️  Please update the following in .env file:"
    echo "   - Google OAuth credentials"
    echo "   - Microsoft OAuth credentials"
    echo "   - Frontend and API URLs for production"
    echo ""
fi

# Install dependencies
echo "📦 Installing dependencies..."
cd backend && npm install && cd ..
cd frontend && npm install && cd ..

# Build and start services
echo "🚀 Starting services..."
docker-compose up -d --build

echo ""
echo "✅ Setup complete!"
echo ""
echo "📱 Access the app at: http://localhost"
echo "🔧 Backend API at: http://localhost:5000"
echo ""
echo "📖 Next steps:"
echo "1. Configure OAuth providers in .env file"
echo "2. For production, update FRONTEND_URL and API URLs"
echo "3. Configure SSL certificates for HTTPS"
echo "4. Check logs: docker-compose logs -f"