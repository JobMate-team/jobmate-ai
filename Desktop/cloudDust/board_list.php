
<?php

$host = "localhost";

$user = "";

$passwd = "";

$dbName = "postboard";

 

@$oDB = new mysqli($host, $user, $passwd, $dbName); // DB에 연결

 

if ($oDB->connect_error) { // DB 연결에 실패하면 오류 출력

    die("DB Error : ".$oDB->connect_error); // 오류 출력

}

 

function sql_query($sql='') { // SQL 쿼리 실행 함수

    global $oDB;

 

    return $oDB->query($sql);

}

 

function sql_get_row($sql='') { // SQL 구문 값 가져오는 함수

    global $oDB;

 

    return $oDB->query($sql)->fetch_array(MYSQLI_ASSOC);

}

 

function sql_get_value($sql='') { // SQL 구문 값을 가져오나 total 숫자만 출력

    global $oDB;

 

    return $oDB->query($sql)->fetch_array(MYSQLI_NUM)[0];

}

?>

<style>

.messageHead {

    border:3px #cccccc solid; // 테두리 설정

    padding:5px; // 폭 설정

    font-size:10pt; // 글자 사이즈 설정

}

 

.boardList {

    font-size:10pt;

    text-align:left;

}

</style>

<div class="messageHead">게시판</div><br/>

<div class="boardList">

<?php

$sql = sql_query("select * from bd__board order by b_idx desc");

 

while ($data = $sql->fetch_assoc()):

?>

    <a href="/?b_idx=<?=$data['b_idx']?>"><?=$data['b_title']?></a><br/>

<?php endwhile?>

</div>