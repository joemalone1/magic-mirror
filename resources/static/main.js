var reminderIdx = 0;
var background = null;
var bkg_height = 1440;
var bkg_width = 2560;

window.onload = function() {
	updateBackground()
    setReminder(daily_reminders[0])
    setTime()
    setInterval(setTime, 5000)
    setInterval(changeReminder, 20000)
    setInterval(updateWeather, 600000)
    setInterval(updateBackground, 600000)
}

function setBackground(background) {
	var backDiv = document.getElementsByClassName("below")
    var bkgdImg = document.createElement("img")

    bkgdImg.setAttribute("src", background);
    bkgdImg.setAttribute("id", "back_img");
    bkgdImg.style.opacity = 0.3;
    backDiv[0].removeChild(backDiv[0].lastElementChild)
    backDiv[0].appendChild(bkgdImg)
}

function resizeBackground() {
	var bkgdImg = document.getElementById("back_img");

	var wOverH = bkgdImg.naturalWidth / bkgdImg.naturalHeight;
    if (bkgdImg.width < bkg_width) {
 	  	bkgdImg.width = bkg_width;
 	  	bkgdImg.height = bkg_width / wOverH; 	
    }
	if (bkgdImg.height < bkg_height) {
    	bkgdImg.height = bkg_height;
    	bkgdImg.width = bkg_height * wOverH;
    }
}

function updateBackground() {
	// get our new background url
	background = fetch('http://localhost:5000/get_background').then(function (response) {
							if (response.ok) {
								return response.json();
							} else {
								return Promise.reject(response);
							}
						}).then(function (data) {
							// call setBackground with the data
							setBackground(data);
						}).catch(function (err) {
							console.warn(err);
						});

	// if the background isn't big enough, zoom in until it is
	setTimeout(resizeBackground, 500);

}

function setReminder(reminder) {
	var reminderTag = document.getElementById("daily_reminder")
	reminderTag.textContent = reminder
}

function changeReminder() {
	var reminderTag = document.getElementById("daily_reminder")
	reminderIdx = reminderIdx + 1 < daily_reminders.length ? reminderIdx + 1 : 0;
	reminderTag.textContent = daily_reminders[reminderIdx]

}

function setTime() {
	var today = new Date();
	var monthMap = {
		0:"January",
		1:"February",
		2:"March",
		3:"April",
		4:"May",
		5:"June",
		6:"July",
		7:"August",
		8:"September",
		9:"October",
		10:"November",
		11:"December"
	}
	var dayMap = {
		0:"Sunday",
		1:"Monday",
		2:"Tuesday",
		3:"Wednesday",
		4:"Thursday",
		5:"Friday",
		6:"Saturday"
	}
	var hours = today.getHours();
	hours = hours < 10 ? "0" + hours : hours;
	var minutes = today.getMinutes();
	minutes = minutes < 10 ? "0" + minutes : minutes;
	var time = hours + ":" + minutes;
	var date = dayMap[today.getDay()] + ", " + monthMap[today.getMonth()] + " " + today.getDate();
	document.getElementById("time").textContent = time;
	document.getElementById("date").textContent = date;
}

function updateWeather() {
	var weather_section = document.getElementById("weather_section");
	var weather_info = fetch('http://localhost:5000/get_weather').then(function (response) {
							if (response.ok) {
								return response.json();
							} else {
								return Promise.reject(response);
							}
						}).then(function (data) {
							weather_section.innerHTML = data;
						}).catch(function (err) {
							console.warn(err);
						});

	return weather_info;
}

function toggleStrikethrough(thisElem) {
	if (thisElem.style.textDecoration == "line-through") {
		thisElem.style.textDecoration = "none";
	} else {
		thisElem.style.textDecoration = "line-through";
	}
	console.log("triggered");
}