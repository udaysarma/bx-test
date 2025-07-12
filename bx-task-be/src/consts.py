websites_to_search = ["https://www.amazon.in", "https://www.flipkart.com", "https://www.reliancedigital.in", "https://www.snapdeal.com", "https://www.shopclues.com", "https://www.tatacliq.com"]
input_eval_js = """
    () => {
      const getCssPath = (el) => {
        if (!(el instanceof Element)) return;
        const path = [];
        while (el.nodeType === Node.ELEMENT_NODE) {
          let selector = el.nodeName.toLowerCase();
          if (el.id) {
            selector += `#${el.id}`;
            path.unshift(selector);
            break;
          } else {
            let sib = el, nth = 1;
            while ((sib = sib.previousElementSibling)) {
              if (sib.nodeName.toLowerCase() === selector) nth++;
            }
            selector += `:nth-of-type(${nth})`;
          }
          path.unshift(selector);
          el = el.parentNode;
        }
        return path.join(' > ');
      };

      return Array.from(document.querySelectorAll('input'))
        .filter(el => {
            const type = (el.getAttribute('type') || 'text').toLowerCase();
            return type === 'text' || type === 'search';
        })
        .map(el => ({
          cssPath: getCssPath(el),
          type: el.type,
          name: el.name || null,
          placeholder: el.placeholder || null
        }));
    }
    """
