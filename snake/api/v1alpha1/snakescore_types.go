package v1alpha1

import metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"

// SnakeScoreSpec is one leaderboard entry.
//
// Scores are ordinary EDA resources: created inside a transaction, written to
// git on commit, and therefore revision-controlled and revertible like any
// other intent in the system.
type SnakeScoreSpec struct {
	// Initials is the three-letter arcade handle, prefilled from the
	// authenticated EDA username by the UI.
	// +kubebuilder:validation:Pattern=`^[A-Z]{3}$`
	// +eda:ui:title="Initials"
	Initials string `json:"initials"`

	// Score is the final score for the run.
	// +kubebuilder:validation:Minimum=0
	// +eda:ui:title="Score"
	Score int `json:"score"`

	// Level reached when the run ended.
	// +kubebuilder:validation:Minimum=1
	// +kubebuilder:validation:Maximum=20
	// +eda:ui:title="Level"
	Level int `json:"level"`

	// Difficulty is the skill ramp the run was played on. Ramps are synthetic
	// and deterministic, so scores are comparable within a difficulty.
	// +kubebuilder:validation:Enum=normal;hard;hez
	// +eda:ui:title="Difficulty"
	Difficulty string `json:"difficulty"`

	// Player is the authenticated EDA user who set the score.
	// +eda:ui:title="Player"
	Player string `json:"player,omitempty"`

	// RecordedAt is an RFC3339 timestamp set by the UI.
	RecordedAt string `json:"recordedAt,omitempty"`

	// FabricNodes records how large the fabric was during the run, so scores
	// stay interpretable after the topology changes.
	// +kubebuilder:validation:Minimum=0
	FabricNodes int `json:"fabricNodes,omitempty"`
}

// SnakeScoreStatus is populated by the leaderboard state intent.
type SnakeScoreStatus struct {
	// Rank within the current difficulty, 1 being the highest.
	Rank int `json:"rank,omitempty"`

	// Accepted is false when validation rejected the entry.
	Accepted bool `json:"accepted,omitempty"`
}

// +kubebuilder:object:root=true
// +kubebuilder:subresource:status
// +kubebuilder:resource:categories={eda,snake}
// +kubebuilder:printcolumn:name="Initials",type=string,JSONPath=`.spec.initials`
// +kubebuilder:printcolumn:name="Score",type=integer,JSONPath=`.spec.score`
// +kubebuilder:printcolumn:name="Level",type=integer,JSONPath=`.spec.level`
// +kubebuilder:printcolumn:name="Mode",type=string,JSONPath=`.spec.difficulty`
// +kubebuilder:printcolumn:name="Player",type=string,JSONPath=`.spec.player`
// +kubebuilder:printcolumn:name="Rank",type=integer,JSONPath=`.status.rank`
type SnakeScore struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   SnakeScoreSpec   `json:"spec,omitempty"`
	Status SnakeScoreStatus `json:"status,omitempty"`
}

// +kubebuilder:object:root=true
type SnakeScoreList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []SnakeScore `json:"items"`
}

func init() { SchemeBuilder.Register(&SnakeScore{}, &SnakeScoreList{}) }
