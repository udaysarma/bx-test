import { type NextRequest, NextResponse } from "next/server"

// Mock product database
const mockProducts = [
  {
    id: 1,
    type: "product",
    title: "Apple MacBook Pro 16-inch M3 Max",
    description: "Powerful laptop with M3 Max chip, 36GB RAM, 1TB SSD. Perfect for professionals and creators.",
    price: 3499.99,
    originalPrice: 3999.99,
    rating: 4.8,
    reviews: 2847,
    brand: "Apple",
    category: "electronics",
    inStock: true,
    freeShipping: true,
    image: "/placeholder.svg?height=300&width=300",
    seller: "Apple Store",
    discount: 13,
    keywords: ["laptop", "macbook", "apple", "computer", "m3", "professional"],
  },
  {
    id: 2,
    type: "product",
    title: "Sony WH-1000XM5 Wireless Headphones",
    description: "Industry-leading noise canceling with premium sound quality and 30-hour battery life.",
    price: 349.99,
    originalPrice: 399.99,
    rating: 4.6,
    reviews: 5234,
    brand: "Sony",
    category: "audio",
    inStock: true,
    freeShipping: true,
    image: "/placeholder.svg?height=300&width=300",
    seller: "Sony Official",
    discount: 12,
    keywords: ["headphones", "wireless", "noise canceling", "sony", "audio", "music"],
  },
  {
    id: 3,
    type: "product",
    title: "Nike Air Jordan 1 Retro High OG",
    description: "Classic basketball sneakers with premium leather construction and iconic design.",
    price: 170.0,
    originalPrice: 170.0,
    rating: 4.7,
    reviews: 1892,
    brand: "Nike",
    category: "footwear",
    inStock: false,
    freeShipping: true,
    image: "/placeholder.svg?height=300&width=300",
    seller: "Nike Store",
    discount: 0,
    keywords: ["shoes", "sneakers", "jordan", "nike", "basketball", "retro"],
  },
  {
    id: 4,
    type: "product",
    title: 'Samsung 65" QLED 4K Smart TV',
    description: "Quantum Dot technology with HDR10+ support and smart TV features powered by Tizen OS.",
    price: 1299.99,
    originalPrice: 1599.99,
    rating: 4.5,
    reviews: 3456,
    brand: "Samsung",
    category: "electronics",
    inStock: true,
    freeShipping: false,
    image: "/placeholder.svg?height=300&width=300",
    seller: "Samsung Electronics",
    discount: 19,
    keywords: ["tv", "television", "samsung", "4k", "smart tv", "qled"],
  },
  {
    id: 5,
    type: "product",
    title: "Dyson V15 Detect Cordless Vacuum",
    description: "Advanced cordless vacuum with laser dust detection and powerful suction technology.",
    price: 649.99,
    originalPrice: 749.99,
    rating: 4.4,
    reviews: 987,
    brand: "Dyson",
    category: "home",
    inStock: true,
    freeShipping: true,
    image: "/placeholder.svg?height=300&width=300",
    seller: "Dyson Official",
    discount: 13,
    keywords: ["vacuum", "cordless", "dyson", "cleaning", "home", "appliance"],
  },
  {
    id: 6,
    type: "product",
    title: "Instant Pot Duo 7-in-1 Electric Pressure Cooker",
    description: "Multi-functional kitchen appliance that pressure cooks, slow cooks, rice cooker, and more.",
    price: 79.99,
    originalPrice: 99.99,
    rating: 4.9,
    reviews: 8765,
    brand: "Instant Pot",
    category: "kitchen",
    inStock: true,
    freeShipping: true,
    image: "/placeholder.svg?height=300&width=300",
    seller: "Instant Brands",
    discount: 20,
    keywords: ["pressure cooker", "instant pot", "kitchen", "cooking", "appliance", "multi-cooker"],
  },
  {
    id: 7,
    type: "product",
    title: "Apple iPhone 15 Pro Max",
    description: "Latest iPhone with titanium design, A17 Pro chip, and advanced camera system.",
    price: 1199.99,
    originalPrice: 1199.99,
    rating: 4.7,
    reviews: 4521,
    brand: "Apple",
    category: "electronics",
    inStock: true,
    freeShipping: true,
    image: "/placeholder.svg?height=300&width=300",
    seller: "Apple Store",
    discount: 0,
    keywords: ["iphone", "apple", "smartphone", "mobile", "phone", "pro max"],
  },
  {
    id: 8,
    type: "product",
    title: "Adidas Ultraboost 22 Running Shoes",
    description: "Premium running shoes with responsive Boost midsole and Primeknit upper.",
    price: 190.0,
    originalPrice: 190.0,
    rating: 4.5,
    reviews: 2156,
    brand: "Adidas",
    category: "footwear",
    inStock: true,
    freeShipping: true,
    image: "/placeholder.svg?height=300&width=300",
    seller: "Adidas Store",
    discount: 0,
    keywords: ["running shoes", "adidas", "ultraboost", "athletic", "sports", "fitness"],
  },
]

export async function GET(request: NextRequest) {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 800 + Math.random() * 700))

  const searchParams = request.nextUrl.searchParams
  const query = searchParams.get("q") || ""
  const category = searchParams.get("category") || "all"
  const brand = searchParams.get("brand") || "all"
  const minRating = Number.parseFloat(searchParams.get("minRating") || "0")
  const sortBy = searchParams.get("sortBy") || "relevance"
  const minPrice = Number.parseFloat(searchParams.get("minPrice") || "0")
  const maxPrice = Number.parseFloat(searchParams.get("maxPrice") || "10000")

  try {
    let filteredProducts = mockProducts

    // Text search
    if (query.trim()) {
      const searchTerms = query.toLowerCase().split(" ")
      filteredProducts = filteredProducts.filter((product) => {
        const searchableText =
          `${product.title} ${product.description} ${product.brand} ${product.category} ${product.keywords?.join(" ")}`.toLowerCase()
        return searchTerms.some((term) => searchableText.includes(term))
      })
    }

    // Category filter
    if (category !== "all") {
      filteredProducts = filteredProducts.filter((product) => product.category.toLowerCase() === category.toLowerCase())
    }

    // Brand filter
    if (brand !== "all") {
      filteredProducts = filteredProducts.filter((product) => product.brand.toLowerCase() === brand.toLowerCase())
    }

    // Rating filter
    if (minRating > 0) {
      filteredProducts = filteredProducts.filter((product) => product.rating >= minRating)
    }

    // Price range filter
    filteredProducts = filteredProducts.filter((product) => product.price >= minPrice && product.price <= maxPrice)

    // Sorting
    switch (sortBy) {
      case "price-low":
        filteredProducts.sort((a, b) => a.price - b.price)
        break
      case "price-high":
        filteredProducts.sort((a, b) => b.price - a.price)
        break
      case "rating":
        filteredProducts.sort((a, b) => b.rating - a.rating)
        break
      case "reviews":
        filteredProducts.sort((a, b) => b.reviews - a.reviews)
        break
      case "relevance":
      default:
        // Keep original order for relevance
        break
    }

    return NextResponse.json({
      products: filteredProducts,
      total: filteredProducts.length,
      query,
      filters: {
        category,
        brand,
        minRating,
        sortBy,
        priceRange: [minPrice, maxPrice],
      },
    })
  } catch (error) {
    console.error("Search API error:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
