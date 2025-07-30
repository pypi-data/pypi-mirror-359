package main

import (
	"C"
)
import (
	"fmt"
	"math"

	"github.com/baahl-nyu/lattigo/v6/circuits/ckks/bootstrapping"
	"github.com/baahl-nyu/lattigo/v6/utils"
)

// Map to store bootstrapping.Evaluators by their slot count
// Initialize the map at package level
var bootstrapperMap = make(map[int]*bootstrapping.Evaluator)

//export NewBootstrapper
func NewBootstrapper(
	LogPs *C.int,
	lenLogPs C.int,
	numSlots C.int,
) {
	slots := int(numSlots)

	if _, exists := bootstrapperMap[slots]; exists {
		return
	}

	// If not initialized for this slot count, create a new one
	logP := CArrayToSlice(LogPs, lenLogPs, convertCIntToInt)

	btpParametersLit := bootstrapping.ParametersLiteral{
		LogN:     utils.Pointy(scheme.Params.LogN()),
		LogP:     logP,
		Xs:       scheme.Params.Xs(),
		LogSlots: utils.Pointy(int(math.Log2(float64(slots)))),
	}

	btpParams, err := bootstrapping.NewParametersFromLiteral(
		*scheme.Params, btpParametersLit)
	if err != nil {
		panic(err)
	}

	btpKeys, _, err := btpParams.GenEvaluationKeys(scheme.SecretKey)
	if err != nil {
		panic(err)
	}

	var btpEval *bootstrapping.Evaluator
	if btpEval, err = bootstrapping.NewEvaluator(btpParams, btpKeys); err != nil {
		panic(err)
	}

	// Store the new evaluator in the map
	bootstrapperMap[slots] = btpEval
}

//export Bootstrap
func Bootstrap(ciphertextID, numSlots C.int) C.int {
	ctIn := RetrieveCiphertext(int(ciphertextID))
	bootstrapper := GetBootstrapper(int(numSlots))

	ctBtp := ctIn.CopyNew()
	ctBtp.LogDimensions.Cols = bootstrapper.LogMaxSlots()

	ctOut, err := bootstrapper.Bootstrap(ctBtp)
	if err != nil {
		panic(err)
	}

	postscale := int(1 << (scheme.Params.LogMaxSlots() - bootstrapper.LogMaxSlots()))
	scheme.Evaluator.Mul(ctOut, postscale, ctOut)

	ctOut.LogDimensions.Cols = scheme.Params.LogMaxSlots()

	idx := PushCiphertext(ctOut)
	return C.int(idx)
}

func GetBootstrapper(numSlots int) *bootstrapping.Evaluator {
	bootstrapper, exists := bootstrapperMap[numSlots]
	if !exists {
		panic(fmt.Errorf("no bootstrapper found for slot count: %d", numSlots))
	}
	return bootstrapper
}

//export DeleteBootstrappers
func DeleteBootstrappers() {
	bootstrapperMap = make(map[int]*bootstrapping.Evaluator)
}
