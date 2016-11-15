/*
 * Здесь находятся расширения прототипов встроенных объектов
 */

Array.max = function(array) {
	return Math.max.apply(Math, array);
};

Array.min = function(array) {
	return Math.min.apply(Math, array);
};

Date.prototype.isoDate = function() {
	return this.getFullYear() + "-" + (parseInt(this.getMonth())+1) + "-" + this.getDate();
}
