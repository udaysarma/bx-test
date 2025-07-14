"use client"

import type React from "react"
import { Search, Filter, TrendingUp, Sparkles } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Product, useSearchStore } from "@/lib/store"

const trendingSearches = [
  "wireless headphones",
  "gaming laptop",
  "smart watch",
  "air fryer",
  "running shoes",
  "4k monitor",
]

export default function SearchPage() {
  const {
    query,
    country,
    results,
    isLoading,
    hasSearched,
    showSuggestions,
    filters,
    totalResults,
    searchTime,
    setQuery,
    setShowSuggestions,
    setFilters,
    searchProducts,
    setCountry,
  } = useSearchStore()

  const handleSearch = async () => {
    if (!query.trim()) return
    await searchProducts(query)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSearch()
    }
  }

  const handleFilterChange = async (filterKey: string, value: any) => {
    setFilters({ [filterKey]: value })

    // Re-search with new filters if we have a query
    if (query.trim()) {
      await searchProducts(query)
    }
  }

  const getPrice = (product: Product) => {
    if (product.price) {
      return product.price
    } 
    return `${product.price_from || product.price_to}`
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse delay-500"></div>
      </div>

      <div className="relative z-10">
        {/* Header */}
        <header className="pt-8 pb-4">
          <div className="max-w-4xl mx-auto px-4">
            <div className="text-center mb-8">
              <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-4">
                SearchVibe
              </h1>
              <p className="text-gray-600 text-lg">Discover amazing products with AI-powered search</p>
            </div>

            {/* Search Bar */}
            <div className="relative max-w-2xl mx-auto">
              <div className="flex gap-3">
                {/* Country Dropdown */}
                <div className="relative">
                  <select
                    value={country}
                    onChange={(e) => {
                      setCountry(e.target.value)
                    }}
                    className="h-16 px-4 pr-8 text-sm rounded-2xl border-2 border-gray-200 focus:border-indigo-500 shadow-lg transition-all duration-300 hover:shadow-xl bg-white appearance-none cursor-pointer min-w-[140px]"
                  >
                    <option value="in">India</option>
                    <option value="us">United States</option>
                    <option value="cn">China</option>
                    <option value="af">Afghanistan</option>
                    <option value="al">Albania</option>
                    <option value="dz">Algeria</option>
                    <option value="ad">Andorra</option>
                    <option value="ao">Angola</option>
                    <option value="ar">Argentina</option>
                    <option value="am">Armenia</option>
                    <option value="au">Australia</option>
                    <option value="at">Austria</option>
                    <option value="az">Azerbaijan</option>
                    <option value="bs">Bahamas</option>
                    <option value="bh">Bahrain</option>
                    <option value="bd">Bangladesh</option>
                    <option value="by">Belarus</option>
                    <option value="be">Belgium</option>
                    <option value="bz">Belize</option>
                    <option value="bj">Benin</option>
                    <option value="bt">Bhutan</option>
                    <option value="bo">Bolivia</option>
                    <option value="ba">Bosnia and Herzegovina</option>
                    <option value="br">Brazil</option>
                    <option value="vg">British Virgin Islands</option>
                    <option value="bn">Brunei</option>
                    <option value="bg">Bulgaria</option>
                    <option value="kh">Cambodia</option>
                    <option value="cm">Cameroon</option>
                    <option value="ca">Canada</option>
                    <option value="cf">Central African Republic</option>
                    <option value="td">Chad</option>
                    <option value="cl">Chile</option>
                    <option value="co">Colombia</option>
                    <option value="cr">Costa Rica</option>
                    <option value="hr">Croatia</option>
                    <option value="cu">Cuba</option>
                    <option value="cy">Cyprus</option>
                    <option value="cz">Czech Republic</option>
                    <option value="dk">Denmark</option>
                    <option value="dk">Denmark</option>
                    <option value="dj">Djibouti</option>
                    <option value="dm">Dominica</option>
                    <option value="do">Dominican Republic</option>
                    <option value="ec">Ecuador</option>
                    <option value="eg">Egypt</option>
                    <option value="ee">Estonia</option>
                    <option value="et">Ethiopia</option>
                    <option value="fj">Fiji</option>
                    <option value="fi">Finland</option>
                    <option value="fr">France</option>
                    <option value="gm">Gambia</option>
                    <option value="ge">Georgia</option>
                    <option value="de">Germany</option>
                    <option value="gh">Ghana</option>
                    <option value="gr">Greece</option>
                    <option value="gt">Guatemala</option>
                    <option value="ht">Haiti</option>
                    <option value="hn">Honduras</option>
                    <option value="hk">Hong Kong</option>
                    <option value="hu">Hungary</option>
                    <option value="is">Iceland</option>
                    <option value="id">Indonesia</option>
                    <option value="iq">Iraq</option>
                    <option value="ie">Ireland</option>
                    <option value="il">Israel</option>
                    <option value="it">Italy</option>
                    <option value="ci">Ivory Coast</option>
                    <option value="jm">Jamaica</option>
                    <option value="jp">Japan</option>
                    <option value="jo">Jordan</option>
                    <option value="kz">Kazakhstan</option>
                    <option value="ke">Kenya</option>
                    <option value="kw">Kuwait</option>
                    <option value="la">Laos</option>
                    <option value="lv">Latvia</option>
                    <option value="lb">Lebanon</option>
                    <option value="li">Liechtenstein</option>
                    <option value="lt">Lithuania</option>
                    <option value="lu">Luxembourg</option>
                    <option value="mk">Macedonia</option>
                    <option value="mg">Madagascar</option>
                    <option value="my">Malaysia</option>
                    <option value="mv">Maldives</option>
                    <option value="ml">Mali</option>
                    <option value="mt">Malta</option>
                    <option value="mu">Mauritius</option>
                    <option value="mx">Mexico</option>
                    <option value="md">Moldova</option>
                    <option value="mn">Mongolia</option>
                    <option value="ma">Morocco</option>
                    <option value="mz">Mozambique</option>
                    <option value="mm">Myanmar</option>
                    <option value="na">Namibia</option>
                    <option value="np">Nepal</option>
                    <option value="nl">Netherlands</option>
                    <option value="nz">New Zealand</option>
                    <option value="ng">Nigeria</option>
                    <option value="no">Norway</option>
                    <option value="om">Oman</option>
                    <option value="pk">Pakistan</option>
                    <option value="pa">Panama</option>
                    <option value="py">Paraguay</option>
                    <option value="pe">Peru</option>
                    <option value="ph">Philippines</option>
                    <option value="pl">Poland</option>
                    <option value="pt">Portugal</option>
                    <option value="pr">Puerto Rico</option>
                    <option value="qa">Qatar</option>
                    <option value="ro">Romania</option>
                    <option value="ru">Russia</option>
                    <option value="sa">Saudi Arabia</option>
                    <option value="sa">Saudi Arabia</option>
                    <option value="sn">Senegal</option>
                    <option value="rs">Serbia</option>
                    <option value="sc">Seychelles</option>
                    <option value="sg">Singapore</option>
                    <option value="sk">Slovakia</option>
                    <option value="si">Slovenia</option>
                    <option value="za">South Africa</option>
                    <option value="kr">South Korea</option>
                    <option value="es">Spain</option>
                    <option value="lk">Sri Lanka</option>
                    <option value="se">Sweden</option>
                    <option value="ch">Switzerland</option>
                    <option value="tw">Taiwan</option>
                    <option value="tz">Tanzania</option>
                    <option value="th">Thailand</option>
                    <option value="tg">Togo</option>
                    <option value="tt">Trinidad and Tobago</option>
                    <option value="tn">Tunisia</option>
                    <option value="tr">Turkey</option>
                    <option value="tm">Turkmenistan</option>
                    <option value="ug">Uganda</option>
                    <option value="ua">Ukraine</option>
                    <option value="ae">United Arab Emirates</option>
                    <option value="gb">United Kingdom</option>
                    <option value="uy">Uruguay</option>
                    <option value="uz">Uzbekistan</option>
                    <option value="ve">Venezuela</option>
                    <option value="vn">Vietnam</option>
                    <option value="zm">Zambia</option>
                    <option value="zw">Zimbabwe</option>
                  </select>
                  {/* Custom dropdown arrow */}
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none">
                    <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>

                {/* Search Input */}
                <div className="relative flex-1">
                  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <Input
                    type="text"
                    placeholder="Search for products..."
                    value={query}
                    onChange={(e) => {
                      setQuery(e.target.value)
                    }}
                    onKeyPress={handleKeyPress}
                    className="pl-12 pr-24 py-4 text-lg rounded-2xl border-2 border-gray-200 focus:border-indigo-500 shadow-lg transition-all duration-300 hover:shadow-xl h-16"
                  />
                  <Button
                    onClick={handleSearch}
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 transition-all duration-300 h-12"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <Sparkles className="w-5 h-5" />
                    )}
                  </Button>
                </div>
              </div>
              <div className="text-center text-sm text-gray-500 mt-2">Search is a bit slow because we search on multiple websites</div>

              {/* Search Suggestions */}
              {showSuggestions && !hasSearched && (
                <Card className="absolute top-full mt-2 w-full z-20 shadow-xl border-0 bg-white/80 backdrop-blur-sm">
                  <CardContent className="p-4">
                    <div className="text-sm text-gray-500 mb-2">Trending searches</div>
                    <div className="space-y-2">
                      {trendingSearches.map((search, index) => (
                        <button
                          key={index}
                          onClick={() => {
                            setQuery(search)
                            setShowSuggestions(false)
                            searchProducts(search)
                          }}
                          className="flex items-center w-full text-left p-2 rounded-lg hover:bg-gray-100 transition-colors duration-200"
                        >
                          <TrendingUp className="w-4 h-4 text-gray-400 mr-3" />
                          {search}
                        </button>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </header>

        {/* Enhanced Product Filters */}

        {/* Loading State */}
        {hasSearched && results.length === 0 &&(
          <div className="max-w-4xl mx-auto px-4">
            <div className="text-center py-12">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full mb-4">
                <div className="w-8 h-8 border-3 border-white border-t-transparent rounded-full animate-spin"></div>
              </div>
              <p className="text-gray-600 text-lg">Searching products...</p>
            </div>
          </div>
        )}

        {/* Product Results */}
        {!isLoading && results.length > 0 && (
          <div className="max-w-6xl mx-auto px-4 pb-12">
            <div className="mb-6 flex justify-between items-center">
              <div className="text-gray-600">
                About {totalResults} products ({searchTime.toFixed(2)} seconds)
              </div>
              {/* <div className="flex gap-2">
                <Button variant="outline" size="sm">
                  Grid View
                </Button>
                <Button variant="outline" size="sm">
                  List View
                </Button>
              </div> */}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {results.toSorted((a: Product, b: Product) => parseFloat(getPrice(a).replace(/[^\d.-]/g, "") || "0") - parseFloat(getPrice(b).replace(/[^\d.-]/g, "") || "0")).map((product, index) => (
                <Card
                  key={product.id}
                  className="group hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 border-0 bg-white/80 backdrop-blur-sm overflow-hidden"
                  style={{
                    animationDelay: `${index * 100}ms`,
                    animation: "fadeInUp 0.6s ease-out forwards",
                  }}
                >
                  <div className="relative">
                    <img
                      src={product.image || "/placeholder-image.png"}
                      alt={product.title}
                      className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                    {/* {product.discount > 0 && (
                      <Badge className="absolute top-2 left-2 bg-red-500 text-white">-{product.discount}%</Badge>
                    )}
                    {!product.inStock && (
                      <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                        <span className="text-white font-semibold">Out of Stock</span>
                      </div>
                    )} */}
                  </div>

                  <CardContent className="p-4">
                    {/* <div className="mb-2">
                      <Badge variant="secondary" className="text-xs">
                        {product.category}
                      </Badge>
                      <span className="text-xs text-gray-500 ml-2">{product.brand}</span>
                    </div> */}

                      <a href={product.link.startsWith('http') ? product.link : product.seller + product.link}>
                        <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2 group-hover:text-indigo-600 transition-colors">
                          {product.title}
                        </h3>
                      </a>

                    {/* <p className="text-sm text-gray-600 mb-3 line-clamp-2">{product.description}</p> */}

                    {/* Rating */}
                    {/* <div className="flex items-center gap-2 mb-3">
                      <div className="flex items-center">
                        {[...Array(5)].map((_, i) => (
                          <span
                            key={i}
                            className={`text-sm ${
                              i < Math.floor(product.rating) ? "text-yellow-400" : "text-gray-300"
                            }`}
                          >
                            ⭐
                          </span>
                        ))}
                      </div>
                      <span className="text-sm text-gray-600">
                        {product.rating} ({product.reviews.toLocaleString()})
                      </span>
                    </div> */}

                    {/* Price */}
                    <div className="flex items-center gap-2 mb-4">
                      {product.price ? (
                        <span className="text-2xl font-bold text-gray-900">{product.price}</span>
                      ) : (
                        <>
                        <span className="text-sm font-bold text-gray-900">from</span><span className="text-2xl font-bold text-gray-900"> {product.price_from}</span>
                        </>
                      )}
                      {/* {product.originalPrice > product.price && (
                        <span className="text-sm text-gray-500 line-through">${product.originalPrice.toFixed(2)}</span>
                      )} */}
                    </div>

                    {/* Seller & Shipping */}
                    <div className="text-xs text-gray-500 mb-3">
                      Sold by {product.seller}
                      {/* {product.freeShipping && <span className="ml-2 text-green-600 font-medium">Free Shipping</span>} */}
                    </div>

                    {/* Action Buttons */}
                    {/* <div className="flex gap-2">
                      <Button
                        className="flex-1 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700"
                        disabled={!product.inStock}
                      >
                        {product.inStock ? "Add to Cart" : "Out of Stock"}
                      </Button>
                      <Button variant="outline" size="icon">
                        ❤️
                      </Button>
                    </div> */}
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* No results state */}
        {/* {!isLoading && hasSearched && results.length === 0 && (
          <div className="max-w-4xl mx-auto px-4 text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No products found</h3>
            <p className="text-gray-600">Try adjusting your search terms or filters</p>
          </div>
        )} */}
      </div>

      <style jsx>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  )
}
