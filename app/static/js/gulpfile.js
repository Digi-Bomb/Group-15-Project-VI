const { src, dest, watch, series } = require("gulp");
const sass = require("gulp-sass")(require("sass"));
const sourcemaps = require("gulp-sourcemaps");

function buildStyles() {
  return src("../scss/custom.scss")
    .pipe(sourcemaps.init())
    .pipe(
      sass({
        outputStyle: "compressed",
        quietDeps: true,
      }).on("error", sass.logError),
    )
    .pipe(sourcemaps.write("."))
    .pipe(dest("../css"));
}

function watchTask() {
  return watch("../scss/custom.scss", buildStyles);
}

exports.default = series(buildStyles, watchTask);
