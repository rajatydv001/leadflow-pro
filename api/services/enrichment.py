import requests
import re
import os
import json
from bs4 import BeautifulSoup
from api.config import Config


class CompanyEnrichmentService:
    def __init__(self):
        self.clearbit_api_key = Config.CLEARBIT_API_KEY
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def enrich_company(self, company_name, website=None):
        enriched_data = {
            'name': company_name,
            'domain': '',
            'industry': '',
            'size': '',
            'location': '',
            'city': '',
            'country': '',
            'description': '',
            'linkedin_url': '',
            'twitter_url': '',
            'logo_url': '',
            'employee_count': '',
            'tech': [],
            'sources': [],
            'founded': '',
            'phone': '',
            'address': '',
            'about': '',
            'services': [],
            'awards': [],
            'team_size': ''
        }

        domain = self._extract_domain(website, company_name)

        # Priority 1: Try Clearbit API if key exists
        if domain and self.clearbit_api_key:
            clearbit_data = self._enrich_clearbit(domain)
            if clearbit_data:
                enriched_data.update(clearbit_data)
                enriched_data['sources'].append('Clearbit API')

        # Priority 2: Try Apollo.io (free API)
        apollo_data = self._enrich_apollo(company_name, domain)
        if apollo_data:
            for key, value in apollo_data.items():
                if not enriched_data.get(key) and value:
                    enriched_data[key] = value
            if 'Apollo.io' not in enriched_data['sources']:
                enriched_data['sources'].append('Apollo.io')

        # Priority 3: Try Google Knowledge Graph API (free, no key needed for small usage)
        if domain and not enriched_data.get('description'):
            kg_data = self._enrich_google_kg(company_name, domain)
            if kg_data:
                for key, value in kg_data.items():
                    if not enriched_data.get(key) and value:
                        enriched_data[key] = value
                enriched_data['sources'].append('Google Knowledge Graph')

        # Priority 4: Enhanced website scraping
        if website:
            website_data = self._scrape_website_comprehensive(website, company_name)
            if website_data:
                for key, value in website_data.items():
                    if not enriched_data.get(key) and value:
                        enriched_data[key] = value
                if 'Website Scraping' not in enriched_data['sources']:
                    enriched_data['sources'].append('Website Scraping')

        # Priority 5: Try scraping from about-us and contact pages
        if website and not enriched_data.get('description'):
            about_data = self._scrape_about_page(website, company_name)
            if about_data:
                for key, value in about_data.items():
                    if not enriched_data.get(key) and value:
                        enriched_data[key] = value
                if 'About Page' not in enriched_data['sources']:
                    enriched_data['sources'].append('About Page')

        # Priority 6: Try LinkedIn company search (if no employee data)
        if not enriched_data.get('employee_count') and company_name:
            linkedin_data = self._search_linkedin(company_name, domain)
            if linkedin_data:
                if enriched_data.get('employee_count'):
                    enriched_data['employee_count'] = linkedin_data.get('employee_count')
                if enriched_data.get('industry') and not linkedin_data.get('industry'):
                    enriched_data['industry'] = linkedin_data.get('industry', '')

        # Fallback: Infer industry from company name
        if not enriched_data['industry']:
            enriched_data['industry'] = self._infer_industry(company_name, enriched_data.get('description', ''))

        # Generate description if still missing
        if not enriched_data['description']:
            enriched_data['description'] = self._generate_description(company_name, enriched_data.get('industry', ''))

        # Set domain from input
        if not enriched_data['domain'] and domain:
            enriched_data['domain'] = domain

        return enriched_data

    def _extract_domain(self, website, company_name):
        if website:
            domain = website.lower()
            domain = re.sub(r'^https?://(www\.)?', '', domain)
            domain = re.sub(r'/.*$', '', domain)
            return domain if domain else None

        company_name_lower = company_name.lower().strip()
        company_name_clean = re.sub(r'[^\w\s]', '', company_name_lower)
        company_name_clean = company_name_clean.replace(' ', '')
        return f"{company_name_clean}.com"

    def _enrich_clearbit(self, domain):
        try:
            headers = {
                'Authorization': f'Bearer {self.clearbit_api_key}',
                'Accept': 'application/json'
            }
            response = requests.get(
                f'https://company.clearbit.com/v2/companies/find?domain={domain}',
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    'name': data.get('name', ''),
                    'domain': data.get('domain', ''),
                    'industry': data.get('category', {}).get('industry', ''),
                    'size': data.get('metrics', {}).get('employees', ''),
                    'location': data.get('geo', {}).get('city', '') + ', ' + data.get('geo', {}).get('country', ''),
                    'city': data.get('geo', {}).get('city', ''),
                    'country': data.get('geo', {}).get('country', ''),
                    'description': data.get('description', ''),
                    'linkedin_url': data.get('linkedin', {}).get('handle', ''),
                    'twitter_url': data.get('twitter', {}).get('handle', ''),
                    'logo_url': data.get('logo', ''),
                    'employee_count': str(data.get('metrics', {}).get('employees', '')),
                    'address': data.get('geo', {}).get('streetAddress', ''),
                    'phone': data.get('phone', '')
                }
        except Exception as e:
            print(f"Clearbit API error: {e}")
        return None

    def _enrich_apollo(self, company_name, domain):
        try:
            url = "https://api.apollo.io/api/v1/mixed_companies/search"
            payload = {
                "query": company_name,
                "page": 1,
                "per_page": 1
            }
            headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('companies') and len(data['companies']) > 0:
                    company = data['companies'][0]
                    result = {
                        'name': company.get('name', ''),
                        'domain': company.get('domain', ''),
                        'industry': company.get('industry', ''),
                        'size': company.get('size', ''),
                        'location': company.get('location', ''),
                        'city': company.get('city', ''),
                        'country': company.get('country', ''),
                        'description': company.get('description', ''),
                        'linkedin_url': company.get('linkedin_url', ''),
                        'twitter_url': company.get('twitter_url', ''),
                        'founded': str(company.get('founded', '')) if company.get('founded') else '',
                        'employee_count': company.get('employee_count', ''),
                        'phone': company.get('phone_number', '')
                    }
                    return result
        except Exception as e:
            print(f"Apollo API error: {e}")
        return None

    def _enrich_google_kg(self, company_name, domain):
        """Use Google's Knowledge Graph API - free with some limits"""
        try:
            # Try to get company info from Google's structured data
            search_url = f"https://www.google.com/search?q={requests.utils.quote(company_name + ' company')}&hl=en"
            
            response = self.session.get(search_url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                data = {}
                
                # Try to find knowledge panel or rich snippets
                for script in soup.find_all('script', type='application/ld+json'):
                    try:
                        content = script.string
                        if content:
                            kg_data = json.loads(content)
                            if isinstance(kg_data, dict):
                                if not data.get('name') and kg_data.get('name'):
                                    data['name'] = kg_data.get('name')
                                if not data.get('description') and kg_data.get('description'):
                                    data['description'] = kg_data.get('description')[:300]
                                if not data.get('industry') and kg_data.get('description'):
                                    industry = self._infer_industry(company_name, kg_data.get('description', ''))
                                    if industry != 'Other':
                                        data['industry'] = industry
                    except:
                        pass
                
                # Extract from visible content
                if not data.get('description'):
                    # Look for company description in search results
                    for div in soup.find_all('div'):
                        text = div.get_text()
                        if text and 100 < len(text) < 400:
                            if 'founded' in text.lower() or 'employees' in text.lower():
                                data['description'] = text[:300]
                                break
                
                # Look for company info cards
                for span in soup.find_all('span'):
                    text = span.get_text()
                    if 'employees' in text.lower():
                        match = re.search(r'(\d+[\d,]*)\s*employees?', text, re.I)
                        if match and not data.get('employee_count'):
                            data['employee_count'] = match.group(1)
                    
                    if 'founded' in text.lower():
                        match = re.search(r'Founded[:\s]*(\d{4})', text, re.I)
                        if match and not data.get('founded'):
                            data['founded'] = match.group(1)
                
                return data if data else None
                
        except Exception as e:
            print(f"Google KG error: {e}")
        
        return None

    def _scrape_website_comprehensive(self, website, company_name):
        if not website:
            return None
            
        if not website.startswith('http'):
            website = 'https://' + website
        
        data = {}
        
        try:
            response = self.session.get(website, timeout=15, allow_redirects=True)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get title
            title_tag = soup.find('title')
            if title_tag and title_tag.text:
                data['name'] = title_tag.text.split('|')[0].split('-')[0].strip()[:50]
            
            # Get meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                data['description'] = meta_desc['content'][:400]
            
            # Get keywords for industry inference
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords and meta_desc and not data.get('description'):
                content = meta_keywords.get('content', '') + ' ' + meta_desc.get('content', '')
                industry = self._infer_industry(company_name, content[:200])
                if industry != 'Other':
                    data['industry'] = industry
            
            # Get favicon/logo
            icon_link = soup.find('link', attrs={'rel': lambda x: x and 'icon' in x})
            if icon_link and icon_link.get('href'):
                favicon = icon_link['href']
                if favicon.startswith('/'):
                    parsed = requests.utils.urlparse(website)
                    favicon = f"{parsed.scheme}://{parsed.netloc}{favicon}"
                data['logo_url'] = favicon
            
            # Look for phone numbers
            phone_numbers = set()
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'tel:' in href:
                    phone = href.replace('tel:', '').strip()
                    if re.match(r'[\d\s\-\+\(\)]{7,20}', phone):
                        phone_numbers.add(re.sub(r'[^\d\+]', '', phone))
            
            if phone_numbers:
                data['phone'] = list(phone_numbers)[0]
            
            # Look for address
            for elem in soup.find_all(['address', 'div', 'span', 'p']):
                text = elem.get_text(strip=True)
                address_patterns = [
                    r'\d+\s+[\w\s]+(?:street|st|avenue|ave|road|rd|boulevard|blvd|drive|dr|lane|ln|way|court|ct|suite|ste|floor|fl)',
                    r'\b[A-Z]{2}\s+\d{5}(-\d{4})?\b',  # State ZIP
                ]
                if any(re.search(p, text, re.I) for p in address_patterns):
                    if len(text) < 200:
                        data['address'] = text
                        break
            
            # Look for social links
            for link in soup.find_all('a', href=True):
                href = link['href'].lower()
                if 'linkedin.com' in href and not data.get('linkedin_url'):
                    data['linkedin_url'] = link['href']
                elif 'twitter.com' in href and not data.get('twitter_url'):
                    data['twitter_url'] = link['href']
            
            # Look for about section
            about_link = None
            for link in soup.find_all('a', href=True):
                text = link.get_text().lower()
                if 'about' in text and 'us' in text:
                    about_link = link['href']
                    break
            
            if about_link:
                if not about_link.startswith('http'):
                    parsed = requests.utils.urlparse(website)
                    about_link = f"{parsed.scheme}://{parsed.netloc}{about_link}"
                
                try:
                    about_response = self.session.get(about_link, timeout=10)
                    if about_response.status_code == 200:
                        about_soup = BeautifulSoup(about_response.text, 'html.parser')
                        
                        # Get about meta description
                        about_meta = about_soup.find('meta', attrs={'name': 'description'})
                        if about_meta and about_meta.get('content'):
                            if not data.get('description') or len(about_meta['content']) > len(data.get('description', '')):
                                data['about'] = about_meta['content'][:500]
                        
                        # Get main content
                        main_content = about_soup.find('main') or about_soup.find('article') or about_soup.find('div', class_=lambda x: x and 'about' in x.lower() if x else False)
                        if main_content:
                            text = main_content.get_text(strip=True)
                            if len(text) > 50:
                                if not data.get('description'):
                                    data['description'] = text[:400]
                except:
                    pass
            
            return data if any(data.values()) else None
                
        except Exception as e:
            print(f"Website scraping error: {e}")
        
        return None

    def _scrape_about_page(self, website, company_name):
        """Scrape the about page for more details"""
        if not website:
            return None
            
        if not website.startswith('http'):
            website = 'https://' + website
        
        # Try common about page paths
        about_paths = ['/about', '/about-us', '/company', '/our-story', '/who-we-are']
        
        for path in about_paths:
            try:
                url = website.rstrip('/') + path
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    data = {}
                    
                    # Get meta description
                    meta = soup.find('meta', attrs={'name': 'description'})
                    if meta and meta.get('content'):
                        data['description'] = meta['content'][:400]
                    
                    # Get main content
                    main = soup.find('main') or soup.find('article') or soup.find('div', class_=lambda x: x and ('content' in x.lower() or 'about' in x.lower()) if x else False)
                    if main:
                        text = main.get_text(' ', strip=True)
                        
                        # Extract founded year
                        founded_match = re.search(r'(?:founded|established|started|created)\s+(?:in\s+)?(?:19|20)\d{2}', text, re.I)
                        if founded_match:
                            year_match = re.search(r'(19|20)\d{2}', founded_match.group())
                            if year_match:
                                data['founded'] = year_match.group()
                        
                        # Extract employee count
                        emp_match = re.search(r'(\d+[\d,]*)\s*(?:employees|staff|people|workers)', text, re.I)
                        if emp_match:
                            data['employee_count'] = emp_match.group(1).replace(',', '')
                        
                        # Get first substantial paragraph as description
                        paragraphs = main.find_all('p')
                        for p in paragraphs:
                            p_text = p.get_text(strip=True)
                            if 100 < len(p_text) < 400:
                                data['about'] = p_text
                                break
                    
                    if data:
                        return data
                        
            except Exception as e:
                continue
        
        return None

    def _search_linkedin(self, company_name, domain):
        """Try to get company info from LinkedIn (public page)"""
        # Note: LinkedIn doesn't allow scraping, but we can check for public company page
        try:
            # Try using Google to find LinkedIn company page
            search_url = f"https://www.google.com/search?q={requests.utils.quote(company_name + ' site:linkedin.com/company')}"
            
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                data = {}
                
                # Look for employee count in search results
                for result in soup.find_all('div'):
                    text = result.get_text()
                    if 'employees' in text.lower():
                        match = re.search(r'(\d+[\d,]*)\s*employees?', text, re.I)
                        if match:
                            data['employee_count'] = match.group(1).replace(',', '')
                            break
                
                return data if data else None
                
        except Exception as e:
            print(f"LinkedIn search error: {e}")
        
        return None

    def _infer_industry(self, company_name, description):
        name_lower = company_name.lower()
        desc_lower = description.lower() if description else ''
        combined = name_lower + ' ' + desc_lower
        
        industries = {
            'Technology': ['tech', 'software', 'digital', 'cloud', 'data', 'ai', 'computer', 'app', 'web', 'it', 'solution', 'saas', 'platform', 'internet', 'cyber', 'automation'],
            'Finance': ['bank', 'finance', 'investment', 'capital', 'fund', 'insurance', 'credit', 'wealth', 'trading', 'financial', 'payment', 'fintech'],
            'Healthcare': ['health', 'medical', 'hospital', 'clinic', 'pharma', 'bio', 'life science', 'wellness', 'drug', 'biotech', 'healthcare', 'clinical'],
            'Consulting': ['consulting', 'advisory', 'strategy', 'management', 'solution', 'professional services', 'audit'],
            'Retail': ['shop', 'store', 'retail', 'e-commerce', 'commerce', 'marketplace', 'shopping', 'fashion', 'clothing'],
            'Manufacturing': ['manufacturing', 'manufacture', 'factory', 'industrial', 'production', 'assembly', 'electronics', 'machinery'],
            'SaaS': ['saas', 'software as a service', 'subscription', 'cloud software', 'enterprise software'],
            'Education': ['education', 'learning', 'training', 'school', 'university', 'academy', 'edtech', 'courses'],
            'Real Estate': ['real estate', 'property', 'housing', 'realty', 'land', 'construction', 'building'],
            'Marketing': ['marketing', 'advertising', 'agency', 'digital marketing', 'seo', 'media', 'brand'],
            'Food': ['food', 'restaurant', 'cafe', 'coffee', 'dining', 'catering', 'beverage', 'agriculture'],
            'Travel': ['travel', 'tourism', 'hotel', 'hospitality', 'airlines', 'transportation', 'logistics'],
        }
        
        for industry, keywords in industries.items():
            if any(kw in combined for kw in keywords):
                return industry
        
        return 'Other'

    def _generate_description(self, company_name, industry):
        templates = {
            'Technology': f"{company_name} is a technology company specializing in innovative software solutions and digital services. They provide cutting-edge technology solutions for businesses and consumers, focusing on delivering exceptional value through technological excellence.",
            'Finance': f"{company_name} is a financial services company providing expert advice and solutions for investment, banking, and wealth management. They offer comprehensive financial services to help clients achieve their financial goals.",
            'Healthcare': f"{company_name} is a healthcare company dedicated to improving health outcomes through medical services and innovative solutions. They are committed to providing exceptional healthcare services.",
            'Consulting': f"{company_name} is a consulting firm providing strategic advice and expert guidance to help businesses achieve their goals. They specialize in delivering tailored solutions for complex business challenges.",
            'Retail': f"{company_name} is a retail company offering quality products and excellent customer service. They are committed to providing an exceptional shopping experience for consumers.",
            'Manufacturing': f"{company_name} is a manufacturing company producing high-quality products for various industries. They maintain the highest standards of quality and efficiency in their production processes.",
            'SaaS': f"{company_name} is a software-as-a-service company providing cloud-based solutions for business productivity. They help organizations streamline their operations with innovative software solutions.",
            'Education': f"{company_name} is an education company committed to learning and development through innovative programs. They provide quality educational services to empower individuals and organizations.",
            'Real Estate': f"{company_name} is a real estate company specializing in property development, management, and investment. They help clients navigate the real estate market with professional expertise.",
            'Marketing': f"{company_name} is a marketing agency specializing in digital marketing, branding, and advertising services. They help businesses grow through innovative marketing strategies.",
            'Food': f"{company_name} is a food and beverage company dedicated to providing quality products and services. They are committed to excellence in the food industry.",
            'Travel': f"{company_name} is a travel and hospitality company providing exceptional services to travelers. They specialize in creating memorable travel experiences.",
            'Other': f"{company_name} is a dynamic company serving customers across various industries with professional solutions. They are committed to delivering excellence in their field."
        }
        return templates.get(industry, templates['Other'])


def get_industry_insights(industry):
    """Return industry-specific insights for PDF generation"""
    insights = {
        'Finance': {
            'trends': [
                'Digital transformation accelerating in banking sector',
                'AI and machine learning adoption for fraud detection',
                'Open banking regulations driving API adoption',
                'Blockchain adoption for cross-border payments',
                'Rise of neobanks and digital-first financial services'
            ],
            'recommendations': [
                'Implement AI-powered customer service chatbots',
                'Develop open banking API integration capabilities',
                'Enhance cybersecurity infrastructure',
                'Create mobile-first digital banking experiences',
                'Invest in blockchain technology for secure transactions'
            ]
        },
        'Technology': {
            'trends': [
                'Cloud-native architecture adoption',
                'DevOps and CI/CD maturity',
                'Security-first development practices',
                'Remote and distributed team management',
                'AI/ML integration in everyday applications'
            ],
            'recommendations': [
                'Migrate to cloud-native infrastructure',
                'Implement comprehensive DevOps practices',
                'Build security-first development culture',
                'Create distributed team collaboration tools',
                'Leverage AI/ML for competitive advantage'
            ]
        },
        'Healthcare': {
            'trends': [
                'Telehealth adoption continuing post-pandemic',
                'AI-assisted diagnostics becoming mainstream',
                'Data privacy and HIPAA compliance focus',
                'Interoperability standards gaining traction',
                'Wearable technology integration in healthcare'
            ],
            'recommendations': [
                'Implement HIPAA-compliant telehealth platform',
                'Develop AI-powered diagnostic assistance tools',
                'Build patient data interoperability features',
                'Create secure messaging and collaboration tools',
                'Integrate wearable device data for personalized care'
            ]
        },
        'Consulting': {
            'trends': [
                'Remote consulting delivery gaining traction',
                'Specialization in digital transformation',
                'Data-driven decision making becoming standard',
                'Sustainability and ESG consulting demand surge',
                'AI-powered consulting tools emergence'
            ],
            'recommendations': [
                'Build specialized digital transformation practice',
                'Invest in data analytics and visualization tools',
                'Develop remote delivery capabilities',
                'Create thought leadership content strategy',
                'Implement AI-assisted consulting tools'
            ]
        },
        'SaaS': {
            'trends': [
                'Product-led growth becoming dominant model',
                'Usage-based pricing gaining popularity',
                'Customer success becoming competitive differentiator',
                'Integration ecosystem expansion',
                'Vertical SaaS specialization increasing'
            ],
            'recommendations': [
                'Implement free trial and freemium models',
                'Build robust integration with popular tools',
                'Develop comprehensive customer success program',
                'Create product usage analytics dashboard',
                'Focus on vertical-specific solutions'
            ]
        },
        'Manufacturing': {
            'trends': [
                'Industry 4.0 and smart factory adoption',
                'IoT and sensor technology integration',
                'Predictive maintenance becoming essential',
                'Supply chain digitalization',
                'Sustainability and green manufacturing focus'
            ],
            'recommendations': [
                'Implement IoT sensor network for monitoring',
                'Deploy predictive maintenance analytics',
                'Build supply chain visibility dashboard',
                'Create digital twin simulation capabilities',
                'Invest in sustainable manufacturing practices'
            ]
        },
        'Retail': {
            'trends': [
                'Omnichannel commerce integration',
                'Personalization through AI/ML',
                'Social commerce and influencer marketing',
                'Inventory optimization with predictive analytics',
                ' sustainability in product sourcing'
            ],
            'recommendations': [
                'Build unified commerce platform',
                'Implement AI-powered personalization engine',
                'Develop social commerce integration',
                'Create real-time inventory management system',
                'Source sustainable products for eco-conscious consumers'
            ]
        },
        'Education': {
            'trends': [
                'Online learning adoption accelerating',
                'AI-powered personalized learning paths',
                'Micro-credential and certification growth',
                'Virtual reality in education',
                'Corporate training digitization'
            ],
            'recommendations': [
                'Develop interactive online learning platforms',
                'Implement AI-powered adaptive learning',
                'Create micro-credential programs',
                'Explore VR/AR for immersive learning',
                'Build corporate training solutions'
            ]
        },
        'Real Estate': {
            'trends': [
                'PropTech revolution and digital transformation',
                'Virtual property tours and digital twins',
                'Sustainable and green building practices',
                'AI-powered property valuation',
                'Remote work impacting office space demand'
            ],
            'recommendations': [
                'Implement virtual property tour technology',
                'Use AI for property valuation and pricing',
                'Develop proptech integration capabilities',
                'Focus on sustainable building practices',
                'Adapt to changing office space needs'
            ]
        },
        'Marketing': {
            'trends': [
                'AI-powered content creation and personalization',
                'Video marketing and short-form content dominance',
                'First-party data strategy importance',
                'Privacy-focused marketing approaches',
                'Influencer marketing maturation'
            ],
            'recommendations': [
                'Implement AI-powered content generation',
                'Build video marketing strategy',
                'Develop first-party data collection',
                'Create privacy-compliant marketing practices',
                'Build long-term influencer partnerships'
            ]
        },
        'Other': {
            'trends': [
                'Digital transformation across all sectors',
                'Data-driven decision making adoption',
                'Remote work enablement',
                'Customer experience focus',
                'Sustainability and ESG integration'
            ],
            'recommendations': [
                'Assess digital maturity and create roadmap',
                'Implement data analytics capabilities',
                'Build remote work infrastructure',
                'Create customer feedback and NPS systems',
                'Integrate sustainability in business strategy'
            ]
        }
    }
    return insights.get(industry, insights['Other'])