<?php
// 요청된 컨텐츠 타입 확인
$type = isset($_GET['type']) ? $_GET['type'] : '';

function callPythonTest() {
    $python = escapeshellcmd('python3');
    $script = escapeshellarg('web_url.py');
    $arg = escapeshellarg('test');

    // web_url.py가 있는 /hanafund 디렉토리에서 실행해야 상대경로가 정상 작동
    $command = "cd /hanafund && PYTHONPATH=. $python $script $arg";
    exec($command . " 2>&1", $output, $statusCode);

    $response = [
        'output' => implode("\n", $output),
        'status' => $statusCode
    ];
    return $response;
}

// 컨텐츠 타입에 따라 다른 내용 반환
switch ($type) {
    case 'intro':
        echo '<h2>서비스 소개</h2>
              <p>하나펀드는 고객의 금융 생활을 더 편리하게 만들어 드립니다. 
              최신 기술을 활용하여 문서 처리와 정보 분석을 자동화하고, 고객에게 맞춤형 서비스를 제공합니다.</p>
              <p>OCR 기술을 통해 문서를 자동으로 인식하고 처리하며, 인공지능 기술로 데이터를 분석하여 최적의 금융 솔루션을 제안합니다.</p>';
        break;
    
    case 'features':
        echo '<h2>기능 안내</h2>
              <ul>
                <li><strong>문서 자동 인식</strong>: OCR 기술을 활용한 문서 자동 인식 및 처리</li>
                <li><strong>데이터 분석</strong>: 고객 데이터 기반 맞춤형 금융 솔루션 제안</li>
                <li><strong>실시간 업데이트</strong>: 금융 시장 변화에 따른 실시간 정보 업데이트</li>
                <li><strong>안전한 데이터 보호</strong>: 고객 정보 보호를 위한 철저한 보안 시스템</li>
              </ul>';
        break;
    
    case 'contact':
        $result = callPythonTest();
        echo "<h2>web_url.py 테스트 호출 결과</h2>";
        echo "<pre>";
        echo "Status Code: " . htmlspecialchars($result['status']) . "\n";
        echo "Output:\n" . htmlspecialchars($result['output']);
        echo "</pre>";
        break;

    default:
        echo '<p>원하시는 정보를 확인하려면 상단의 버튼을 클릭하세요.</p>';
}
?> 