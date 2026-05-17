import requests
import re
from bs4 import BeautifulSoup
from config import Config


class CompanyEnrichmentService:
    def __init__(self):
        self.clearbit_api_key = Config.CLEARBIT_API_KEY

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
            'sources': []
        }

        domain = self._extract_domain(website, company_name)

        if domain and self.clearbit_api_key:
            clearbit_data = self._enrich_clearbit(domain)
            if clearbit_data:
                enriched_data.update(clearbit_data)
                enriched_data['sources'].append('Clearbit API')

        if not enriched_data['domain'] and domain:
            enriched_data['domain'] = domain
            enriched_data['sources'].append('Input provided')

        if website and not enriched_data.get('description'):
            website_data = self._scrape_website(website)
            if website_data:
                if not enriched_data['description'] and website_data.get('description'):
                    enriched_data['description'] = website_data['description']
                if not enriched_data['industry'] and website_data.get('industry'):
                    enriched_data['industry'] = website_data['industry']
                enriched_data['sources'].append('Website scraping')

        if not enriched_data['industry']:
            enriched_data['industry'] = self._infer_industry(company_name, enriched_data.get('description', ''))

        if not enriched_data['description']:
            enriched_data['description'] = self._generate_description(company_name, enriched_data.get('industry', ''))

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
                    'domain': data.get('domain', ''),
                    'name': data.get('name', ''),
                    'industry': data.get('category', {}).get('industry', ''),
                    'size': data.get('category', {}).get('sector', ''),
                    'location': f"{data.get('geo', {}).get('city', '')}, {data.get('geo', {}).get('country', '')}" if data.get('geo') else '',
                    'city': data.get('geo', {}).get('city', ''),
                    'country': data.get('geo', {}).get('country', ''),
                    'description': data.get('description', ''),
                    'linkedin_url': data.get('linkedin', {}).get('handle', ''),
                    'twitter_url': data.get('twitter', {}).get('handle', ''),
                    'logo_url': data.get('logo', ''),
                    'employee_count': data.get('metrics', {}).get('employeesRange', ''),
                    'tech': data.get('tech', [])
                }
        except Exception as e:
            print(f"Clearbit API error: {e}")

        return None

    def _scrape_website(self, url):
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                title = soup.find('title')
                title_text = title.get_text().strip() if title else ''

                meta_desc = soup.find('meta', attrs={'name': 'description'})
                desc = meta_desc.get('content', '') if meta_desc else ''

                return {
                    'title': title_text,
                    'description': desc[:300] if desc else ''
                }

        except Exception as e:
            print(f"Website scraping error: {e}")

        return None

    def _infer_industry(self, company_name, description):
        company_lower = company_name.lower()
        desc_lower = description.lower() if description else ''

        industry_keywords = {
            'Finance': ['bank', 'financial', 'capital', 'investment', 'insurance', 'credit', 'wealth'],
            'Consulting': ['consulting', 'advisory', 'management', 'strategy'],
            'SaaS': ['software', 'cloud', 'platform', 'saas', 'app', 'digital'],
            'Healthcare': ['health', 'medical', 'pharma', 'biotech', 'hospital', 'clinic'],
            'Manufacturing': ['manufacturing', 'factory', 'industrial', 'production'],
            'Retail': ['retail', 'store', 'shop', 'e-commerce', 'commerce'],
            'Technology': ['tech', 'technology', 'it', 'software', 'data', 'ai']
        }

        text_to_check = company_lower + ' ' + desc_lower

        for industry, keywords in industry_keywords.items():
            if any(kw in text_to_check for kw in keywords):
                return industry

        return 'Other'

    def _generate_description(self, company_name, industry):
        if industry and industry != 'Other':
            return f"{company_name} is a {industry} company operating in the business services sector. We have prepared this personalized audit to help optimize their business operations and identify growth opportunities."

        return f"{company_name} is a business operating in the commercial sector. This personalized audit report has been prepared to provide strategic insights and recommendations for business growth."


def get_industry_insights(industry):
    return Config.INDUSTRY_INSIGHTS.get(industry, Config.INDUSTRY_INSIGHTS['Other'])