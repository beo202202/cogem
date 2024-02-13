// home.js

var currentImageIndex = 0;
var imageFiles = [];

function showToast(message) {
  var toast = document.getElementById("toast");
  toast.innerHTML = message;
  toast.className = "show";
  setTimeout(function () {
    toast.className = toast.className.replace("show", "");
  }, 3000);
}
function checkCoreInfo() {
  var inputFiles = document.getElementById("files"); // 파일 입력을 위한 요소 선택
  var radioButtons = document.querySelectorAll(
    'input[type="radio"][name="class"]'
  ); // 'class' 이름을 가진 모든 라디오 버튼 선택
  var radioButtonChecked = Array.from(radioButtons).some(
    (radio) => radio.checked
  ); // 선택된 라디오 버튼이 있는지 확인

  if (inputFiles.files.length === 0) {
    // input에 파일이 선택되었는지 확인
    showToast("파일을 선택해주세요.");
    return false; // 파일이 없으면 함수 실행을 중지
  } else if (!radioButtonChecked) {
    // 라디오 버튼이 선택되었는지 확인
    showToast("직업을 선택해주세요.");
    return false; // 라디오 버튼이 선택되지 않았으면 함수 실행을 중지
  }
  showGIF();

  var formData = new FormData(document.getElementById("uploadForm")); // FormData 객체 생성
  // 이후 AJAX 요청 로직을 계속합니다.
  $.ajax({
    url: "/core_info_check",
    type: "POST",
    processData: false, // FormData를 사용할 때 필수
    contentType: false, // FormData를 사용할 때 필수
    data: formData,
    success: function (response) {
      // 성공 시 처리 로직
      showToast("코어 정보 준비 완료");
    },
    error: function (error) {
      // 에러 처리 로직
      showToast("코어 정보 준비 실패");
      console.error("Error:", error);
    },
  });
}

$("#coreInfoCheckButton").click(function () {
  transformImages();
});

function previewImage() {
  showToast("Previewing...");
  var preview = document.getElementById("image-preview");
  imageFiles = document.getElementById("files").files;

  if (imageFiles.length > 0) {
    preview.style.display = "block"; // 이미지가 선택되었을 때 미리보기 표시
    showImage(0); // 첫 번째 이미지 표시

    // 이미지가 여러 개일 경우에만 버튼 표시
    if (imageFiles.length > 1) {
      document
        .querySelectorAll(".button")
        .forEach((btn) => (btn.style.display = "block"));
    } else {
      document
        .querySelectorAll(".button")
        .forEach((btn) => (btn.style.display = "none"));
    }
  } else {
    preview.style.display = "none"; // 이미지가 없을 때 미리보기 숨김
  }
}

function showNextImage() {
  if (imageFiles.length > 1) {
    currentImageIndex = (currentImageIndex + 1) % imageFiles.length;
    showImage(currentImageIndex);
  }
}

function showPreviousImage() {
  if (imageFiles.length > 1) {
    currentImageIndex =
      (currentImageIndex - 1 + imageFiles.length) % imageFiles.length;
    showImage(currentImageIndex);
  }
}

function showImage(index) {
  var preview = document.getElementById("image-preview");
  var reader = new FileReader();
  reader.onload = function (e) {
    preview.querySelector("img").src = e.target.result;
  };
  reader.readAsDataURL(imageFiles[index]);
}

var clickedButtonValue = ""; // 클릭된 버튼 값을 저장할 변수

function validateForm() {
  var files = document.forms["uploadForm"]["files"].value;
  if (files == "") {
    showToast("파일을 선택해주세요.");
    return false;
  }

  if (clickedButtonValue === "분석하기") {
    showToast("분석하기");
    showGIF();
    return true;
  } else if (clickedButtonValue === "테스트") {
    showToast("테스트");
    // AJAX 요청 보내기
    showGIF();
    sendAjaxRequest();
    return false;
  } else if (clickedButtonValue === "코어 분석") {
    var radios = document.forms["uploadForm"]["coreOption"];
    var isChecked = false;
    for (var i = 0; i < radios.length; i++) {
      if (radios[i].checked) {
        isChecked = true;
        break;
      }
    }
    if (!isChecked) {
      showToast("직업을 선택해주세요.");
      return false;
    }
    showToast("코어 분석");
    showGIF();
    return true;
  }
  return false;
}

//코어 젬스톤 사용 gif
function showGIF() {
  var gifContainer = document.getElementById("gif-container");
  var files = document.getElementById("files").files;
  var gifURL = "";
  var displayDuration = 2000; // 기본 2초
  var timestamp = new Date().getTime(); // 현재 시간을 밀리초로 가져옵니다.

  if (files.length >= 1 && files.length <= 5) {
    gifURL = "static/etc/코어젬스톤-core-gem-stone.gif?time=" + timestamp;
    displayDuration = 2000; // 2초
  } else if (files.length >= 6 && files.length <= 10) {
    gifURL = "static/etc/코어젬스톤-core-gem-stone-75%.gif?time=" + timestamp;
    displayDuration = 3000; // 3초
  } else if (files.length >= 11 && files.length <= 15) {
    gifURL = "static/etc/코어젬스톤-core-gem-stone-50%.gif?time=" + timestamp;
    displayDuration = 4000; // 4초
  }

  if (gifURL) {
    gifContainer.innerHTML = '<img src="' + gifURL + '" alt="Loading..." />';
    // 지정된 시간 후 GIF 제거
    setTimeout(function () {
      gifContainer.innerHTML = ""; // GIF 컨테이너를 비웁니다.
    }, displayDuration);
  } else {
    gifContainer.innerHTML = ""; // 파일이 없거나 조건에 맞지 않는 경우 GIF 컨테이너를 비웁니다.
  }
}

function sendAjaxRequest() {
  var formData = new FormData(document.getElementById("uploadForm"));
  formData.append("action", clickedButtonValue);

  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/upload", true);

  xhr.onload = function () {
    if (this.status == 200) {
      var response = JSON.parse(this.responseText);
      document.getElementById("result2").innerHTML = response.html;
    }
  };

  xhr.send(formData);
}

function openTab(evt, tabName) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";
}

function getSelectedClassName() {
  // className 변수 초기화
  var className = "";

  // 모든 직업 그룹 가져오기
  var groups = document.getElementsByClassName("optionGroup");

  // 각 그룹을 반복합니다.
  for (var i = 0; i < groups.length; i++) {
    // 현재 그룹이 표시되어 있는지 확인
    if (groups[i].style.display === "block") {
      // 표시된 그룹 내의 모든 라디오 버튼 가져오기
      var radios = groups[i].getElementsByTagName("input");

      // 라디오 버튼을 반복하여 체크된 버튼을 찾습니다.
      for (var j = 0; j < radios.length; j++) {
        if (radios[j].type === "radio" && radios[j].checked) {
          // 체크된 라디오 버튼의 값을 className에 할당합니다.
          className = radios[j].value;
          break; // 선택한 라디오가 발견되면 루프 종료
        }
      }
    }
  }

  // Return the selected class name
  return className;
}

function addContentToResult2(className, main, sub1, sub2, info) {
  // var className = "Test_Eunwol";
  var className = getSelectedClassName();
  console.log(className);

  var result2 = document.getElementById("result2");
  if (result2) {
    result2.innerHTML = `
      <div class="row">
        <div class="cell">${className}</div>
      </div>
      <div class="row">
        <div class="cell" id="coreInfoWrapper">
          <div id="coreInfo">
            <table border="1">
              <thead>
                <tr>
                  <th>No.</th>
                  <th>코어</th>
                  <th>스킬1</th>
                  <th>스킬2</th>
                  <th>스킬3</th>
                  <th>정보</th>
                </tr>
              </thead>
              <tbody id="coreInfo_tbody">
                <!-- 분석된 이미지 데이터를 행으로 추가 -->
                <!-- 서버로부터 받아온 데이터를 기반으로 자바스크립트를 통해 여기에 행을 추가할 예정 -->
              </tbody>
            </table>
          </div>
        </div>
        <div class="cell">
          2칸-2
        </div>
      </div>
    `;
  }
}

function addTableToResult2(
  no,
  originalImageSrc,
  mainImageSrc,
  subImage1Src,
  subImage2Src,
  info
) {
  // 부모 요소를 가져오는 로직 추가
  const coreInfoTable = document.getElementById("coreInfo_tbody");

  // 부모 요소가 존재하는지 확인
  if (coreInfoTable) {
    // 부모 요소가 존재하면 행 추가
    const row = document.createElement("tr");

    // 행 내부 셀 추가
    const noCell = document.createElement("td");
    noCell.textContent = no;
    row.appendChild(noCell);

    const originalImageCell = document.createElement("td");
    const originalImage = document.createElement("img");
    originalImage.src = originalImageSrc;
    originalImageCell.appendChild(originalImage);
    row.appendChild(originalImageCell);

    const mainImageCell = document.createElement("td");
    const mainImage = document.createElement("img");
    mainImage.src = mainImageSrc;
    mainImageCell.appendChild(mainImage);
    row.appendChild(mainImageCell);

    const subImage1Cell = document.createElement("td");
    const subImage1 = document.createElement("img");
    subImage1.src = subImage1Src;
    subImage1Cell.appendChild(subImage1);
    row.appendChild(subImage1Cell);

    const subImage2Cell = document.createElement("td");
    const subImage2 = document.createElement("img");
    subImage2.src = subImage2Src;
    subImage2Cell.appendChild(subImage2);
    row.appendChild(subImage2Cell);

    const infoCell = document.createElement("td");
    infoCell.textContent = info;
    row.appendChild(infoCell);

    // 행을 테이블에 추가
    coreInfoTable.appendChild(row);
  } else {
    console.error("Core Info Table not found");
  }
}

// 캐시 버스터를 사용하여 이미지 URL 생성 함수
function createImageUrl(basePath, cacheBuster) {
  return basePath ? `${basePath}?v=${cacheBuster}` : "";
}

function testCompareImages() {
  showToast("testCompareImages()");
  var radioButtons = document.querySelectorAll(
    'input[type="radio"][name="class"]'
  ); // 'class' 이름을 가진 모든 라디오 버튼 선택
  var radioButtonChecked = Array.from(radioButtons).some(
    (radio) => radio.checked
  ); // 선택된 라디오 버튼이 있는지 확인

  if (!radioButtonChecked) {
    // 라디오 버튼이 선택되었는지 확인
    showToast("직업을 선택해주세요.");
    return false; // 라디오 버튼이 선택되지 않았으면 함수 실행을 중지
  }

  var formData = new FormData();
  var selectedValue = $("#characterSelect").val();
  console.log(selectedValue);
  formData.append("occupation", selectedValue);

  var className = getSelectedClassName();
  console.log(className);
  formData.append("className", className);
  // formData.append('file', $('#file-input')[0].files[0]);
  // formData.append('username', '사용자명');
  // var formData = "static/processed/image_01/extracted_01.png";

  // or

  // var jsonData = {
  //   username: "사용자명",
  //   password: "비밀번호",
  // };

  // or
  // var queryString = "username=사용자명&password=비밀번호";
  $.ajax({
    url: "/test_compare_images",
    type: "POST",
    processData: false,
    contentType: false,
    data: formData,

    // contentType: "application/json",
    // data: JSON.stringify(jsonData),

    // data: queryString,
    success: function (response) {
      showToast("성공함");
      console.log("비교 결과:", response);

      // 결과 처리 로직...
      // results 리스트를 가져와서 보유한 코어정보 테이블에 추가
      let currentNo = 1; // 초기 No. 값
      for (const result of response) {
        const image_path = result.image_path;
        const extracted_image_paths = [
          result.extracted_image_path1,
          result.extracted_image_path2,
          result.extracted_image_path3,
        ];

        // 캐시 버스터를 생성하여 이미지 URL에 추가
        const cacheBuster = new Date().getTime();
        const origin_imgUrl = createImageUrl(image_path, cacheBuster);

        // 추출된 이미지 URL 생성
        const extracted_imgUrls = extracted_image_paths.map((path) =>
          createImageUrl(path, cacheBuster)
        );

        const match = result.match;

        // 새로운 행을 보유한 코어정보 테이블에 추가하고 No. 증가
        addTableToResult2(
          currentNo.toString(), // No.
          origin_imgUrl, // 코어 이미지
          extracted_imgUrls[0], // 스킬1 (캐시 버스터가 추가된 URL)
          extracted_imgUrls[1], // 스킬2 (미정)
          extracted_imgUrls[2], // 스킬3 (미정)
          match // 추가 정보 (비교 결과)
        );

        currentNo++; // No. 증가
      }
    },
    error: function (error) {
      console.error("Error:", error);
    },
  });
}

function showOptions(value) {
  // 모든 직업 그룹을 숨깁니다.
  var groups = document.getElementsByClassName("optionGroup");
  for (var i = 0; i < groups.length; i++) {
    groups[i].style.display = "none";
    // Deselect all radio buttons in each group.
    var radios = groups[i].getElementsByTagName("input");
    for (var j = 0; j < radios.length; j++) {
      if (radios[j].type === "radio") {
        radios[j].checked = false;
      }
    }
  }

  // 선택된 값에 따라 특정 그룹을 표시합니다.
  if (value === "adventurer") {
    document.getElementById("adventurerOptions").style.display = "block";
  } else if (value === "hero") {
    document.getElementById("heroOptions").style.display = "block";
  }
}

// 페이지 로드 시 실행되는 함수들
document.addEventListener("DOMContentLoaded", pageLoaded);

function pageLoaded() {
  // 데이터 입력 탭을 기본으로 열기
  document.getElementById("defaultOpen").click();
  // 드롭 다운 리스트 중 '모험가'를 선택
  showOptions(document.getElementById("characterSelect").value);

  // 이미지 프리뷰 앞뒤에 이벤트 리스너 추가
  document
    .getElementById("button prev")
    .addEventListener("click", showPreviousImage);
  document
    .getElementById("button next")
    .addEventListener("click", showNextImage);

  // '코어 정보 확인하기' 버튼에 이벤트 리스너 추가
  document
    .getElementById("checkCoreInfo")
    .addEventListener("click", checkCoreInfo);
  // 'makeTable' 버튼에 이벤트 리스너 추가
  document
    .getElementById("makeTable")
    .addEventListener("click", addContentToResult2);
  // 'files' 에 change 이벤트 리스너 추가
  document.getElementById("files").addEventListener("change", previewImage);
  // 'characterSelect' 에 change 이벤트 리스너 추가
  document
    .getElementById("characterSelect")
    .addEventListener("change", function (event) {
      showOptions(this.value);
    });

  // 'viewAnalyze' 버튼에 이벤트 리스너 추가
  document
    .getElementById("viewAnalyze")
    .addEventListener("click", testCompareImages);
}
