function getCookie (name) {
	let value = `; ${document.cookie}`;
	let parts = value.split(`; ${name}=`);
	if (parts.length === 2) return parts.pop().split(';').shift();
}

function setCookie(name, val, expiryDays =30)
{
    // expires in two weeks: 60 seconds x 60 minutes x 24 hours x 14 days
    // we'll look at the math behind this in the next section
    document.cookie = `${name}=${val}; path=/; max-age=${60 * 60 * 24 * expiryDays};`;
}