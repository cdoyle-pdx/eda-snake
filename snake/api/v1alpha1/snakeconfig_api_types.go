/*
Copyright 2026.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package v1alpha1

// SnakeConfigSpec holds the settings an operator may want to change without
// rebuilding the container image.
//
// The UI finds this CR with an EQL query rather than a fixed path, because the
// query endpoint is not namespace-qualified: that way an admin can create it
// wherever they like and the game still picks it up. If no SnakeConfig exists,
// the defaults below apply and the app works out of the box.
//
// Every field is optional. The UI clamps values it cannot render rather than
// trusting them, so a bad edit degrades to the default instead of breaking the
// game.
// +eda:ui:defaultcolumns=.metadata.name
// +eda:ui:defaultcolumns=.metadata.namespace
// +eda:ui:defaultcolumns=.spec.scoreNamespace
// +eda:ui:defaultcolumns=.spec.boardSize
// +eda:ui:defaultcolumns=.spec.defaultDifficulty
type SnakeConfigSpec struct {
	// ScoreNamespace is where SnakeScore CRs are written and read.
	//
	// Scores deliberately live in ONE namespace so a single leaderboard covers
	// the event however many fabrics the lab has - a run against one fabric
	// still competes with a run against another. Changing this after scores
	// exist leaves the old ones behind in the previous namespace.
	// +kubebuilder:validation:Pattern=`^[a-z0-9]([-a-z0-9]*[a-z0-9])?$`
	// +kubebuilder:validation:MaxLength=63
	// +kubebuilder:default=eda
	ScoreNamespace string `json:"scoreNamespace,omitempty"`

	// BoardSize is how many entries the leaderboard shows.
	// +kubebuilder:validation:Minimum=3
	// +kubebuilder:validation:Maximum=50
	// +kubebuilder:default=10
	BoardSize int `json:"boardSize,omitempty"`

	// DefaultDifficulty is the skill ramp the menu opens on. Players can still
	// pick any mode; this only sets the starting selection, which is useful for
	// an unattended booth machine.
	// +kubebuilder:validation:Enum=normal;hard;hez
	// +kubebuilder:default=normal
	DefaultDifficulty string `json:"defaultDifficulty,omitempty"`
}

// SnakeConfigStatus is intentionally empty.
//
// SnakeConfig is pure configuration: it is read by the browser, and no intent
// reconciles it, so there is nothing for a controller to report back. The type
// exists because edabuilder's generated base types reference both a Spec and a
// Status for every kind.
type SnakeConfigStatus struct {
}
