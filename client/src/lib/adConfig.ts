/**
 * Ad Revenue Optimization Configuration - ADSTERRA
 * 
 * Adsterra provides higher CPM rates ($5-20+ per 1000 views) for trading/finance niche
 * Supports multiple ad formats: banners, pop-unders, native, push notifications
 * 
 * Setup Instructions:
 * 1. Create Adsterra account: https://adsterra.com/
 * 2. Create zones in dashboard (get zone IDs for each placement)
 * 3. Replace YOUR_ADSTERRA_ZONE_ID_* with your actual zone IDs
 * 4. Monitor earnings in dashboard - adjust placements based on performance
 */

export const AD_CONFIG = {
  // Adsterra Configuration (Primary Revenue Source)
  adsterra: {
    enabled: true,
    accountEmail: "your@email.com",
    zones: {
      // Header banner (728x90 leaderboard - high visibility)
      headerBanner: {
        zoneId: "YOUR_ADSTERRA_ZONE_ID_HEADER",
        type: "banner",
        size: [728, 90],
        position: "top",
        label: "Sponsored",
        hideOnMobile: false
      },
      // Sidebar rectangle (300x250 - HIGHEST EARNER)
      sidebarRectangle: {
        zoneId: "YOUR_ADSTERRA_ZONE_ID_SIDEBAR",
        type: "display",
        size: [300, 250],
        position: "right",
        label: "Promoted",
        hideOnMobile: false
      },
      // Footer banner
      footerBanner: {
        zoneId: "YOUR_ADSTERRA_ZONE_ID_FOOTER",
        type: "banner",
        size: [728, 90],
        position: "bottom",
        label: "Advertisement",
        hideOnMobile: true
      },
      // Pop-under (high eCPM - can increase revenue 40-60%)
      popUnder: {
        zoneId: "YOUR_ADSTERRA_ZONE_ID_POPUNDER",
        type: "pop-under",
        position: "overlay",
        frequency: "once-per-session",
        delay: 30000,
        enabled: true
      },
      // Native ad (in-feed, blends with content)
      nativeAd: {
        zoneId: "YOUR_ADSTERRA_ZONE_ID_NATIVE",
        type: "native",
        position: "inline",
        placement: "metrics-section",
        label: "Recommended"
      },
      // Push notifications (excellent retention + earnings)
      pushNotifications: {
        zoneId: "YOUR_ADSTERRA_ZONE_ID_PUSH",
        type: "push",
        enabled: false,
        frequency: "max-5-per-day",
        title: "Aztryx Market Alert"
      }
    },
    tracking: {
      trackImpressions: true,
      trackClicks: true,
      trackConversions: true
    }
  },

  // Engagement Features (Increases Revenue 2-3x)
  engagement: {
    // Push notifications for market alerts
    pushNotifications: {
      enabled: false,
      title: "Aztryx Market Alert",
      icon: "/favicon.svg",
      vibrate: [200, 100, 200],
      alerts: {
        vixSpike: {
          enabled: true,
          threshold: 10,
          cooldown: 3600000
        },
        priceAlert: {
          enabled: true,
          threshold: 2,
          cooldown: 600000
        },
        dailySummary: {
          enabled: true,
          scheduledTime: "09:15",
          cooldown: 86400000
        },
        marketCloseSummary: {
          enabled: true,
          scheduledTime: "15:35",
          cooldown: 86400000
        }
      }
    },

    // Email newsletter for repeat visits
    emailNewsletter: {
      enabled: true,
      title: "Get Daily Trading Insights",
      subtitle: "Real-time VIX analysis + market signals",
      description: "Join traders receiving daily market insights",
      placeholders: [
        { position: "sidebar-bottom", variant: "card" },
        { position: "exit-intent", variant: "modal" },
        { position: "after-5-visits", variant: "sticky-bar" }
      ],
      fields: ["email", "name"],
      incentive: "Instant VIX alerts + daily signals (no spam)"
    },

    // Social sharing buttons (go viral)
    socialSharing: {
      enabled: true,
      title: "Share with Traders",
      platforms: [
        {
          name: "twitter",
          icon: "twitter",
          color: "#1DA1F2",
          url: "https://twitter.com/intent/tweet",
          text: "Real-time NIFTY & BANKNIFTY analysis on Aztryx",
          hashtags: "#Trading,#NIFTY,#StockMarket,#India,#OptionsTrading"
        },
        {
          name: "linkedin",
          icon: "linkedin",
          color: "#0A66C2",
          url: "https://www.linkedin.com/sharing/share-offsite/",
          text: "Professional trading dashboard for Indian markets"
        },
        {
          name: "whatsapp",
          icon: "whatsapp",
          color: "#25D366",
          url: "https://wa.me/?text=",
          text: "Check live NIFTY trading data on Aztryx"
        },
        {
          name: "telegram",
          icon: "send",
          color: "#0088cc",
          url: "https://t.me/share/url",
          text: "Trading dashboard with real-time market data"
        },
        {
          name: "facebook",
          icon: "facebook",
          color: "#1877F2",
          url: "https://www.facebook.com/sharer/sharer.php",
          text: "Real-time market analysis tool"
        }
      ],
      positions: ["topRight", "afterMetrics", "sidebar"]
    },

    // Gamification for repeat visits
    gamification: {
      enabled: true,
      features: {
        dailyStreak: {
          enabled: true,
          bonusAtDay: [7, 14, 30, 90, 365],
          reward: "unlock-premium-for-1-day",
          notification: true
        },
        achievements: {
          enabled: true,
          badges: [
            {
              id: "first-check",
              title: "Market Watcher",
              description: "Check market data on first day",
              icon: "eye"
            },
            {
              id: "week-streak",
              title: "Consistent Trader",
              description: "7-day visiting streak",
              icon: "flame"
            },
            {
              id: "analyst",
              title: "Data Analyst",
              description: "View volume profile 10 times",
              icon: "chart-bar"
            },
            {
              id: "early-bird",
              title: "Early Bird",
              description: "Visit before 09:20 AM",
              icon: "sunrise"
            },
            {
              id: "night-owl",
              title: "Night Owl",
              description: "Visit after market close",
              icon: "moon"
            },
            {
              id: "social-butterfly",
              title: "Social Butterfly",
              description: "Share on social media 5 times",
              icon: "share-2"
            }
          ]
        },
        points: {
          enabled: true,
          activities: {
            dailyVisit: 10,
            shareOnSocial: 50,
            addToWatchlist: 5,
            viewAdvancedMetrics: 3,
            subscribeNewsletter: 100,
            achievementUnlocked: 25
          },
          rewards: [
            { points: 100, reward: "unlock-premium-1-day" },
            { points: 500, reward: "unlock-premium-1-week" }
          ]
        },
        leaderboard: {
          enabled: true,
          metric: "visits_this_month",
          displayTopN: 10,
          refreshInterval: 3600000
        }
      }
    },

    // Referral program (go viral)
    referrals: {
      enabled: true,
      title: "Refer & Earn",
      description: "Invite traders, earn 500 points per successful referral",
      shareMessage: "Join Aztryx for real-time NIFTY trading analysis",
      incentive: {
        referrer: "500-points-and-premium-1-week",
        referee: "premium-1-day"
      }
    },

    // Personalization
    personalization: {
      enabled: true,
      localStorage: {
        rememberTickers: true,
        rememberTheme: true,
        rememberChartSettings: true,
        rememberAlerts: true
      },
      features: {
        smartRecommendations: true,
        watchlists: true,
        customAlerts: true,
        userPreferences: true,
        searchHistory: true
      }
    }
  },

  // Monetization Strategies (Premium Revenue)
  monetization: {
    // Freemium model
    freemium: {
      enabled: true,
      tier: "free",
      upgrade: {
        title: "Upgrade to Premium",
        description: "Unlock advanced features",
        cta: "Upgrade Now"
      },
      features: {
        free: [
          "Real-time VIX & price data",
          "Basic volume profile",
          "Simple price charts",
          "3 watchlist items",
          "General market alerts",
          "Mobile access"
        ],
        premium: [
          "All free features +",
          "Advanced volume profile",
          "Custom alerts (50+)",
          "Historical data export (CSV/Excel)",
          "Unlimited watchlists",
          "Ad-free experience",
          "Advanced indicators",
          "Priority support",
          "Early access to new features"
        ]
      },
      pricing: {
        monthly: {
          price: 499,
          currency: "INR",
          billingCycle: "month"
        },
        quarterly: {
          price: 1299,
          currency: "INR",
          billingCycle: "3-months",
          savings: "13%"
        },
        annual: {
          price: 4999,
          currency: "INR",
          billingCycle: "year",
          savings: "17%"
        }
      }
    },

    // Affiliate partnerships
    affiliates: {
      enabled: true,
      program: "Earn commissions by referring brokers",
      partners: [
        {
          name: "Zerodha",
          logo: "/logos/zerodha.png",
          link: "https://zerodha.com?ref=aztryx",
          commission: "20-30% per signup",
          placement: "sidebar-bottom"
        },
        {
          name: "Angel Broking",
          logo: "/logos/angel.png",
          link: "https://angelbroking.com?ref=aztryx",
          commission: "25% per signup",
          placement: "footer"
        },
        {
          name: "Shoonya",
          logo: "/logos/shoonya.png",
          link: "https://shoonya.angelbroking.com",
          commission: "15% per signup",
          placement: "sidebar"
        },
        {
          name: "TradingView",
          logo: "/logos/tradingview.png",
          link: "https://tradingview.com?ref=aztryx",
          commission: "5-10% commission",
          placement: "chart-area"
        }
      ]
    },

    // Sponsored content
    sponsored: {
      enabled: true,
      acceptSponsors: true,
      minimumCPM: 2,
      categories: ["Trading Tools", "Financial Education", "Brokers", "Trading Strategy"],
      disclaimer: "This is sponsored content"
    }
  },

  // Optimization Settings
  optimization: {
    lazyLoadAds: true,
    adRefreshInterval: 30000,
    showAdsAfterInteraction: false,
    frequencyCap: {
      enabled: true,
      maxImpressions: 8
    },
    blockWords: [
      "casino",
      "gambling",
      "crypto",
      "forex",
      "loans"
    ],
    preferredCategories: [
      "Financial Services",
      "Brokers",
      "Trading Tools",
      "Investment",
      "Insurance",
      "Banking"
    ]
  },

  // High-CPM Ad Sizes (by earnings potential)
  highCpmSizes: [
    [300, 250],
    [336, 280],
    [728, 90],
    [970, 90],
    [320, 50],
    [320, 600]
  ],

  // Performance Tracking
  tracking: {
    enabled: true,
    analytics: {
      trackImpressions: true,
      trackClicks: true,
      trackViewTime: true,
      trackEngagement: true,
      trackConversions: true
    },
    events: [
      "ad-impression",
      "ad-click",
      "ad-close",
      "user-engagement",
      "page-view",
      "email-signup",
      "social-share",
      "premium-click"
    ]
  },

  // SEO & Content Strategy
  seo: {
    enabled: true,
    targeting: {
      keywords: [
        "NIFTY trading",
        "BANKNIFTY trading",
        "stock market analysis",
        "volatility analysis",
        "trading signals India",
        "market technical analysis",
        "options trading",
        "price action trading"
      ],
      description: "Real-time NIFTY & BANKNIFTY trading dashboard with live volatility analysis, volume profile, and market signals for Indian traders.",
      authors: ["Aztryx Trading Team"]
    }
  },

  // A/B Testing (optimize revenue)
  abTesting: {
    enabled: true,
    experiments: [
      {
        id: "header-ad-placement",
        variant: "sticky-header",
        audience: "50%",
        metric: "eCPM"
      },
      {
        id: "pop-under-timing",
        variant: "30sec-delay",
        audience: "50%",
        metric: "CTR"
      }
    ]
  }
};

/**
 * USER ENGAGEMENT CONFIG
 * 
 * Higher engagement = more page views = more ad impressions = higher revenue
 * Target: 3-5 minutes average session time
 */
export const ENGAGEMENT_CONFIG = {
  bouncePrevention: {
    enabled: true,
    strategies: [
      "push-notifications",
      "email-signup",
      "social-sharing",
      "gamification",
      "related-content"
    ]
  },

  retentionBoosters: {
    pushNotifications: true,
    emailNewsletter: true,
    gamification: true,
    personalizedContent: true
  },

  targetMetrics: {
    avgSessionDuration: 180,
    pageViewsPerSession: 4,
    returnVisitRate: 0.35,
    bounceRate: 0.25
  }
};

/**
 * REVENUE PROJECTIONS (with all features enabled)
 * 
 * Week 1: 100-200 daily users, $5-20/day
 * Week 2: 300-500 daily users, $30-80/day
 * Month 1: 500-1000 daily users, $100-300/day
 * Month 3: 3000-5000 daily users, $500-1500/day
 * Month 6: 10000+ daily users, $2000-5000/day
 * 
 * Key drivers: Fresh data (VIX), PWA, mobile optimization, social viral, SEO
 */
