;(function () {
  try {
    const current = document.currentScript
    if (!current) {
      console.warn('[UserInsight] Unable to locate tracking script element')
      return
    }

    const scriptUrl = new URL(current.src)
    const uid = scriptUrl.searchParams.get('uid')
    if (!uid) {
      console.warn('[UserInsight] Missing uid in tracking script query params')
      return
    }

    const apiBase = scriptUrl.origin.replace(/\/$/, '')
    const sessionKey = `userinsight_session_${uid}`
    const randomSession =
      typeof crypto !== 'undefined' && crypto.randomUUID
        ? () => crypto.randomUUID()
        : () => `${Date.now()}_${Math.random().toString(16).slice(2)}`

    let sessionId = localStorage.getItem(sessionKey)
    if (!sessionId) {
      sessionId = randomSession()
      localStorage.setItem(sessionKey, sessionId)
    }

    const defaultMetadata = () => ({
      page_url: window.location.href,
      referrer: document.referrer || null,
      user_agent: navigator.userAgent,
      screen: `${window.screen.width}x${window.screen.height}`,
    })

    const transmit = (payload) => {
      const body = JSON.stringify(payload)
      const url = `${apiBase}/collect?uid=${encodeURIComponent(uid)}`

      if (navigator.sendBeacon) {
        const sent = navigator.sendBeacon(url, new Blob([body], { type: 'application/json' }))
        if (sent) return
      }

      fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body,
        keepalive: true,
        credentials: 'omit',
      }).catch((err) => console.warn('[UserInsight] Failed to send event', err))
    }

    const sendEvent = (eventType, metadata) => {
      const mergedMeta = Object.assign({}, defaultMetadata(), metadata || {})
      const payload = {
        session_id: sessionId,
        event_type: eventType,
        page: window.location.pathname,
        website: window.location.origin,
        timestamp: new Date().toISOString(),
        metadata: mergedMeta,
      }

      if (typeof mergedMeta.scroll_depth === 'number') {
        payload.scroll_depth = mergedMeta.scroll_depth
      }

      transmit(payload)
    }

    sendEvent('page_view')

    document.addEventListener(
      'click',
      (event) => {
        const target = event.target
        if (!target) return
        sendEvent('click', {
          tag: target.tagName,
          id: target.id || null,
          class: target.className || null,
          text: (target.innerText || '').trim().slice(0, 80),
        })
      },
      true,
    )

    let scrollTimeout
    document.addEventListener(
      'scroll',
      () => {
        clearTimeout(scrollTimeout)
        scrollTimeout = setTimeout(() => {
          const scrolled = window.scrollY + window.innerHeight
          const docHeight = document.documentElement.scrollHeight || document.body.scrollHeight
          const depth = Math.min(100, (scrolled / docHeight) * 100)
          sendEvent('scroll', { scroll_depth: Math.round(depth) })
        }, 600)
      },
      { passive: true },
    )
  } catch (error) {
    console.warn('[UserInsight] Tracking script error', error)
  }
})()

