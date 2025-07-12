import { create } from "zustand"

export interface Product {
  id: number
  type: string
  title: string
  description: string
  price: string
  originalPrice: number
  rating: number
  reviews: number
  brand: string
  category: string
  inStock: boolean
  freeShipping: boolean
  image: string
  seller: string
  discount: number
  link: string
}

export interface SearchFilters {
  category: string
  brand: string
  minRating: number
  sortBy: string
  priceRange: [number, number]
  country: string
}

interface SearchState {
  // State
  query: string
  results: Product[]
  isLoading: boolean
  hasSearched: boolean
  showSuggestions: boolean
  filters: SearchFilters
  totalResults: number
  searchTime: number
  timeoutId: any
  searchId?: string | null
  country: string

  // Actions
  setQuery: (query: string) => void
  setShowSuggestions: (show: boolean) => void
  setFilters: (filters: Partial<SearchFilters>) => void
  searchProducts: (query: string) => Promise<void>
  clearResults: () => void
  setCountry: (country: string) => void
}

export const useSearchStore = create<SearchState>((set, get) => ({
  // Initial state
  query: "",
  results: [],
  isLoading: false,
  hasSearched: false,
  showSuggestions: false,
  totalResults: 0,
  searchTime: 0,
  searchId: null,
  country: "in",
  timeoutId: null,
  filters: {
    category: "all",
    brand: "all",
    minRating: 0,
    sortBy: "relevance",
    priceRange: [0, 5000],
    country: "US"
  },

  setCountry: (country: string) => {
    set((state) => ({
      country: country
    }))
  },

  // Actions
  setQuery: (query) => set({ query }),

  setShowSuggestions: (show) => set({ showSuggestions: show }),

  setFilters: (newFilters) =>
    set((state) => ({
      filters: { ...state.filters, ...newFilters },
    })),

  searchProducts: async (searchQuery) => {
    console.log("Searching for:", searchQuery)
    const startTime = Date.now()
    set({ isLoading: true, hasSearched: true, showSuggestions: false })
    const { timeoutId, searchId,country } = get()
    // Clear any existing timeout
    if (timeoutId) {
      clearTimeout(timeoutId)
      set({ timeoutId: null })
    }
    try {
      const { filters } = get()

      const updateResults = async () => {
        const params = new URLSearchParams({
          q: searchQuery,
          country,
        })

        const response = await fetch(`http://localhost:8000/api/search?${params}`)

        if (!response.ok) {
          throw new Error("Search failed")
        }

        const data = await response.json()
        const searchTime = (Date.now() - startTime) / 1000

        const timeoutid = setTimeout(async () => {
          await updateResults()
        }, 4000)

        set({
          results: data.products,
          totalResults: data.total,
          searchId: data.searchId,
          searchTime,
          isLoading: false,
          timeoutId: timeoutid,
        })
      }

      await updateResults();      
    } catch (error) {
      console.error("Search error:", error)
      set({
        results: [],
        totalResults: 0,
        searchTime: 0,
        isLoading: false,
      })
    }
  },

  clearResults: () =>
    set({
      results: [],
      hasSearched: false,
      totalResults: 0,
      searchTime: 0,
    }),
}))
