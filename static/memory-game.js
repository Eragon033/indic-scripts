var match = {};
j = 0;
for (let i = 0; i < letters.length; i++) {
    document.getElementById("card" + (i + 1)).addEventListener('click', function () {
        document.getElementById(letters[i]).src = "static/letters/" + letters[i] + ".png";
        match[letters[i]] = 1;
        if (Object.keys(match).length == 2) {
            const k = Object.keys(match);
            var l1 = k[0];
            var l2 = k[1];
            var start = l1.slice(0, 2);
            if (l2.startsWith(start)) {
                setTimeout(matched, 2000, l1, l2);
                j += 1;
                document.getElementById("points").innerHTML = "Points: " + j;
            }
            else {
                setTimeout(unmatched, 2000, l1, l2);
            }
            delete match[l1];
            delete match[l2];
        }
    });
}
function matched(a, b) {
    document.getElementById(a).style.visibility = 'hidden';
    document.getElementById(b).style.visibility = 'hidden';
}
function unmatched(a, b) {
    document.getElementById(a).src = "static/back.jpg";
    document.getElementById(b).src = "static/back.jpg";
}