# 한국투자증권 오픈API 개발자 가이드

## 📋 목차
1. [API 개요](#api-개요)
2. [계좌 연결 방식](#계좌-연결-방식)
3. [실투자 vs 모의투자](#실투자-vs-모의투자)
4. [주식 자동매매 프로그램 개발 가이드](#주식-자동매매-프로그램-개발-가이드)
5. [API 적용 방법](#api-적용-방법)
6. [화면 출력 구현](#화면-출력-구현)

---

## 🔍 API 개요

### 한국투자증권 오픈API란?
한국투자증권 오픈API는 개인 투자자가 자신의 계좌 정보를 조회하고 주식 거래를 할 수 있도록 제공하는 공식 API 서비스입니다.

### 주요 기능
- **계좌 정보 조회**: 잔고, 보유종목, 수익률 등
- **주식 거래**: 매수/매도 주문, 주문 취소/정정
- **시세 조회**: 실시간 현재가, 차트 데이터
- **자동매매**: 프로그램을 통한 자동 거래

---

## 🔗 계좌 연결 방식

### 1. 계좌번호 구성
```
전체 계좌번호 = 계좌번호(8자리) + 계좌상품코드(2자리)
예시: 12345678-01
```

### 2. 필요한 정보
- **API 키 (APP_KEY)**: 한국투자증권에서 발급받은 애플리케이션 키
- **API 시크릿 (APP_SECRET)**: API 키와 함께 사용하는 비밀키
- **계좌번호**: 본인의 계좌번호 앞 8자리
- **계좌상품코드**: 계좌번호 뒤 2자리 (보통 "01")

### 3. 환경변수 설정
```env
# 모의투자용
KIS_APP_KEY_PAPER="your-paper-api-key"
KIS_APP_SECRET_PAPER="your-paper-api-secret"
KIS_ACCOUNT_NO_PAPER="12345678"
KIS_ACCOUNT_CODE_PAPER="01"

# 실투자용
KIS_APP_KEY_REAL="your-real-api-key"
KIS_APP_SECRET_REAL="your-real-api-secret"
KIS_ACCOUNT_NO_REAL="12345678"
KIS_ACCOUNT_CODE_REAL="01"
```

---

## 🎯 실투자 vs 모의투자

### 모의투자 (Paper Trading)
- **목적**: 실제 돈 없이 거래 연습
- **특징**: 
  - 실제 시장 데이터 사용
  - 가상의 돈으로 거래
  - 손실 위험 없음
- **사용 시기**: API 테스트, 전략 검증

### 실투자 (Real Trading)
- **목적**: 실제 돈으로 거래
- **특징**:
  - 실제 계좌 사용
  - 실제 손익 발생
  - 신중한 접근 필요
- **사용 시기**: 검증된 전략으로 실제 투자

---

## 🤖 주식 자동매매 프로그램 개발 가이드

### 1. 기본 구조
```python
class StockTradingBot:
    def __init__(self):
        self.api_client = None
        self.trading_strategy = None
    
    def connect_account(self):
        """계좌 연결"""
        pass
    
    def get_market_data(self):
        """시장 데이터 조회"""
        pass
    
    def analyze_market(self):
        """시장 분석"""
        pass
    
    def execute_trade(self):
        """거래 실행"""
        pass
```

### 2. 자동매매 로직 예시
```python
def auto_trading_strategy():
    # 1. 현재 보유 종목 조회
    holdings = get_holdings()
    
    # 2. 관심 종목 시세 조회
    target_stocks = ['005930', '000660', '035420']  # 삼성전자, SK하이닉스, NAVER
    current_prices = {}
    
    for stock in target_stocks:
        price_data = get_current_price(stock)
        current_prices[stock] = price_data
    
    # 3. 매매 조건 확인
    for stock in target_stocks:
        if should_buy(stock, current_prices[stock]):
            place_buy_order(stock, quantity=10)
        elif should_sell(stock, current_prices[stock]):
            place_sell_order(stock, quantity=10)
```

### 3. 리스크 관리
- **손절매**: 일정 손실 시 자동 매도
- **익절매**: 목표 수익 달성 시 자동 매도
- **포지션 크기 제한**: 한 번에 거래할 금액 제한
- **일일 거래 한도**: 하루 최대 거래 횟수 제한

---

## 🔧 API 적용 방법

### 1. 토큰 발급
```python
def get_access_token():
    url = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": "YOUR_API_KEY",
        "appsecret": "YOUR_API_SECRET"
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(body))
    return response.json()['access_token']
```

### 2. 잔고 조회
```python
def get_balance(access_token):
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/trading/inquire-balance"
    headers = {
        "authorization": f"Bearer {access_token}",
        "appKey": "YOUR_API_KEY",
        "appSecret": "YOUR_API_SECRET",
        "tr_id": "TTTC8434R"
    }
    params = {
        "CANO": "계좌번호",
        "ACNT_PRDT_CD": "계좌상품코드",
        "AFHR_FLPR_YN": "N",
        "INQR_DVSN": "01"
    }
    
    response = requests.get(url, headers=headers, params=params)
    return response.json()
```

### 3. 주문 실행
```python
def place_order(access_token, symbol, quantity, price, order_type="BUY"):
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/trading/order-cash"
    headers = {
        "authorization": f"Bearer {access_token}",
        "appKey": "YOUR_API_KEY",
        "appSecret": "YOUR_API_SECRET",
        "tr_id": "TTTC0802U" if order_type == "BUY" else "TTTC0801U"
    }
    body = {
        "CANO": "계좌번호",
        "ACNT_PRDT_CD": "계좌상품코드",
        "PDNO": symbol,
        "ORD_DVSN": "00",  # 지정가
        "ORD_QTY": str(quantity),
        "ORD_UNPR": str(price)
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(body))
    return response.json()
```

---

## 📊 화면 출력 구현

### 1. 웹 인터페이스 구성
```html
<!-- 수익 현황 대시보드 -->
<div class="dashboard">
    <!-- 계좌 정보 -->
    <div class="account-info">
        <h3>계좌 정보</h3>
        <p>계좌번호: <span id="accountNo"></span></p>
        <p>투자모드: <span id="tradingMode"></span></p>
    </div>
    
    <!-- 수익 요약 -->
    <div class="profit-summary">
        <div class="card">
            <h4>총 평가금액</h4>
            <p id="totalBalance">0원</p>
        </div>
        <div class="card">
            <h4>총 수익</h4>
            <p id="totalProfit">0원</p>
        </div>
        <div class="card">
            <h4>수익률</h4>
            <p id="profitRate">0%</p>
        </div>
    </div>
    
    <!-- 보유 종목 목록 -->
    <div class="holdings-list">
        <h3>보유 종목</h3>
        <table id="holdingsTable">
            <thead>
                <tr>
                    <th>종목코드</th>
                    <th>종목명</th>
                    <th>보유수량</th>
                    <th>매수가</th>
                    <th>현재가</th>
                    <th>수익</th>
                    <th>수익률</th>
                </tr>
            </thead>
            <tbody id="holdingsBody">
            </tbody>
        </table>
    </div>
</div>
```

### 2. JavaScript 데이터 처리
```javascript
async function loadProfitData() {
    try {
        const response = await fetch('/api/profit');
        const data = await response.json();
        
        // 모의투자 데이터 표시
        if (data.paper) {
            displayAccountData(data.paper, 'paper');
        }
        
        // 실투자 데이터 표시
        if (data.real) {
            displayAccountData(data.real, 'real');
        }
        
    } catch (error) {
        console.error('데이터 로드 실패:', error);
    }
}

function displayAccountData(data, mode) {
    // 계좌 정보 업데이트
    document.getElementById('accountNo').textContent = data.account_info.acc_no;
    document.getElementById('tradingMode').textContent = 
        mode === 'paper' ? '모의투자' : '실투자';
    
    // 수익 요약 업데이트
    document.getElementById('totalBalance').textContent = 
        formatCurrency(data.total_balance);
    document.getElementById('totalProfit').textContent = 
        formatCurrency(data.total_profit);
    
    // 수익률 계산 및 표시
    const profitRate = data.total_purchase_amount > 0 ? 
        (data.total_profit / data.total_purchase_amount * 100) : 0;
    document.getElementById('profitRate').textContent = 
        profitRate.toFixed(2) + '%';
    
    // 보유 종목 목록 업데이트
    updateHoldingsTable(data.holdings);
}

function updateHoldingsTable(holdings) {
    const tbody = document.getElementById('holdingsBody');
    tbody.innerHTML = '';
    
    holdings.forEach(holding => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${holding.symbol}</td>
            <td>${holding.name}</td>
            <td>${holding.quantity.toLocaleString()}</td>
            <td>${formatCurrency(holding.purchase_price)}</td>
            <td>${formatCurrency(holding.current_price)}</td>
            <td class="${holding.profit >= 0 ? 'text-green-600' : 'text-red-600'}">
                ${formatCurrency(holding.profit)}
            </td>
            <td class="${holding.profit_rate >= 0 ? 'text-green-600' : 'text-red-600'}">
                ${holding.profit_rate.toFixed(2)}%
            </td>
        `;
        tbody.appendChild(row);
    });
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('ko-KR').format(amount) + '원';
}
```

### 3. 실시간 데이터 업데이트
```javascript
// 5초마다 데이터 새로고침
setInterval(loadProfitData, 5000);

// 웹소켓을 통한 실시간 업데이트 (고급 기능)
function setupWebSocket() {
    const ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.type === 'price_update') {
            updateStockPrice(data.symbol, data.price);
        }
    };
}
```

---

## ⚠️ 주의사항

### 1. 보안
- API 키는 절대 공개하지 마세요
- 환경변수나 설정 파일에 안전하게 저장하세요
- HTTPS를 사용하여 통신하세요

### 2. API 사용 제한
- 초당 요청 수 제한이 있습니다
- 일일 API 호출 한도가 있습니다
- 실투자 시 신중하게 접근하세요

### 3. 테스트
- 반드시 모의투자로 충분히 테스트하세요
- 소액으로 시작하여 점진적으로 확대하세요
- 백테스팅을 통한 전략 검증이 필요합니다

---

## 📞 지원 및 문의

- **한국투자증권 개발자센터**: https://developers.koreainvestment.com
- **API 문서**: https://apiportal.koreainvestment.com
- **기술지원**: 1544-9000

---

*이 가이드는 한국투자증권 오픈API를 활용한 주식 자동매매 프로그램 개발을 위한 기본적인 내용을 담고 있습니다. 실제 투자에 적용하기 전에 충분한 테스트와 검증이 필요합니다.* 