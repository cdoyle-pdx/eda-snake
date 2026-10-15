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

// SnakeScoreSpec is one leaderboard entry.
//
// Scores are ordinary EDA resources: created inside a transaction, written to
// git on commit, and therefore revision-controlled like any other intent.
//
// SnakeScore is the ONLY record the leaderboard keeps. There were once a
// SnakeLeaderboard config CR and a SnakeLeaderboardState CR whose status held a
// pre-ranked board, because an EDA config intent cannot write status. Nothing
// needed that: the EDA dashboard sorts these rows itself and ten entries sort
// instantly in the browser.
// +eda:ui:defaultcolumns=.metadata.name
// +eda:ui:defaultcolumns=.metadata.namespace
// +eda:ui:defaultcolumns=.spec.initials
// +eda:ui:defaultcolumns=.spec.score
// +eda:ui:defaultcolumns=.spec.level
// +eda:ui:defaultcolumns=.spec.difficulty
// +eda:ui:defaultcolumns=.spec.player
// +eda:ui:defaultcolumns=.spec.recordedAt
type SnakeScoreSpec struct {
	// Initials is the name on the board, 1-10 capital letters, prefilled from the
	// authenticated EDA username by the UI.
	// +kubebuilder:validation:Pattern=`^[A-Z]{1,10}$`
	Initials string `json:"initials"`

	// Score is the final score for the run.
	// +kubebuilder:validation:Minimum=0
	Score int `json:"score"`

	// Level reached when the run ended.
	// +kubebuilder:validation:Minimum=1
	// +kubebuilder:validation:Maximum=20
	Level int `json:"level"`

	// Difficulty is the skill ramp the run was played on. Ramps are synthetic
	// and deterministic, so scores are comparable within a difficulty.
	// +kubebuilder:validation:Enum=normal;hard;hez
	Difficulty string `json:"difficulty"`

	// Player is the authenticated EDA user who set the score.
	Player string `json:"player,omitempty"`

	// RecordedAt is an RFC3339 timestamp set by the UI. It is also the
	// tie-breaker when two runs share a score: the earlier run ranks higher.
	RecordedAt string `json:"recordedAt,omitempty"`

	// FabricNodes records how large the fabric was during the run, so scores
	// stay interpretable after the topology changes.
	// +kubebuilder:validation:Minimum=0
	FabricNodes int `json:"fabricNodes,omitempty"`
}

// SnakeScoreStatus is no longer populated.
//
// It was written by the leaderboard state intent, which has been removed along
// with the two leaderboard CRDs. Ranking now happens in the browser at read
// time. The fields are kept so existing CRs stay valid; nothing reads them.
//
// Worth stating plainly: validation is therefore advisory. The intent used to
// reject impossible scores server-side and nothing does now, so a determined
// player with devtools could POST a fabricated entry. That is an accepted
// trade for a booth leaderboard, not an oversight.
type SnakeScoreStatus struct {
	// Rank within the current difficulty, 1 being the highest.
	Rank int `json:"rank,omitempty"`

	// Accepted is false when validation rejected the entry.
	Accepted bool `json:"accepted,omitempty"`
}
