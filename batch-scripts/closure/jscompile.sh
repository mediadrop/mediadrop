closure-library/closure/bin/build/closurebuilder.py \
--namespace=mcore \
--root=mediadrop/public/scripts/mcore/ \
--root=closure-library/ \
--output_mode=compiled \
-c batch-scripts/closure/compiler/compiler.jar \
--compiler_flags="--js=closure-library/closure/goog/deps.js" \
--compiler_flags="--output_wrapper='(function(){%output%})();'" \
--compiler_flags="--compilation_level=ADVANCED_OPTIMIZATIONS" \
--compiler_flags="--warning_level=VERBOSE" \
--compiler_flags="--jscomp_warning=checkTypes" \
--compiler_flags="--jscomp_warning=accessControls" \
--compiler_flags="--jscomp_warning=missingProperties" \
--compiler_flags="--externs=mediadrop/public/scripts/mcore/externs.js" \
> mediadrop/public/scripts/mcore-compiled.js
#--compiler_flags="--jscomp_error=checkTypes" \
#--compiler_flags="--formatting=PRETTY_PRINT" \
#--compiler_flags="--formatting=PRINT_INPUT_DELIMITER" \
