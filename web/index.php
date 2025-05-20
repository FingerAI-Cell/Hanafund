<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>하나펀드 서비스</title>
    <style>
        body {
            font-family: 'Malgun Gothic', sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .button-container {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        button {
            padding: 10px 20px;
            background-color: #008485;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #006666;
        }
        .content-area {
            min-height: 300px;
            border: 1px solid #ddd;
            padding: 20px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        .debug-info {
            margin-top: 20px;
            padding: 10px;
            background-color: #f5f5f5;
            border: 1px solid #ddd;
            font-family: monospace;
            white-space: pre;
            overflow: auto;
        }
    </style>
</head>
<body>
    <h1>하나펀드 서비스</h1>
    
    <div class="button-container">
        <button id="btn1">서비스 소개</button>
        <button id="btn2">기능 안내</button>
        <button id="btn3">문의하기</button>
    </div>
    
    <div class="content-area" id="content">
        여기를 클릭하여 원하는 정보를 확인하세요.
    </div>
    
    <?php
    // 진단 정보 출력
    echo '<div class="debug-info">';
    echo 'PHP 버전: ' . phpversion() . "\n";
    echo 'Server Software: ' . $_SERVER['SERVER_SOFTWARE'] . "\n";
    echo 'Document Root: ' . $_SERVER['DOCUMENT_ROOT'] . "\n";
    echo 'Script Filename: ' . $_SERVER['SCRIPT_FILENAME'] . "\n";
    echo 'Current Working Directory: ' . getcwd() . "\n";
    echo 'File Permissions: ' . substr(sprintf('%o', fileperms(__FILE__)), -4) . "\n";
    echo 'User Info: ' . get_current_user() . "\n";
    
    // 디렉토리 읽기 테스트
    echo 'Directory Listing: ';
    if ($handle = opendir('.')) {
        while (false !== ($entry = readdir($handle))) {
            echo "$entry, ";
        }
        closedir($handle);
    }
    echo '</div>';
    ?>
    
    <script>
        document.getElementById('btn1').addEventListener('click', function() {
            fetch('content.php?type=intro')
                .then(response => response.text())
                .then(data => {
                    document.getElementById('content').innerHTML = data;
                });
        });
        
        document.getElementById('btn2').addEventListener('click', function() {
            fetch('content.php?type=features')
                .then(response => response.text())
                .then(data => {
                    document.getElementById('content').innerHTML = data;
                });
        });
        
        document.getElementById('btn3').addEventListener('click', function() {
            fetch('content.php?type=contact')
                .then(response => response.text())
                .then(data => {
                    document.getElementById('content').innerHTML = data;
                });
        });
    </script>
</body>
</html> 