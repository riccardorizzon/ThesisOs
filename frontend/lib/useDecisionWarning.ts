"use client";

import { useMemo } from "react";
import type { ContextPacket, EntityScope } from "@/lib/contextClient";
import {
  findConflictingDecision,
  parseDecisionsFromPacket,
  type DecisionView,
} from "@/lib/decisionClient";

export type DecisionWarningState = {
  active: boolean;
  message: string | null;
  decisionId?: string;
  decision?: DecisionView;
};

export type UseDecisionWarningInput = {
  packet?: ContextPacket | null;
  entity?: EntityScope | null;
  selectionText?: string | null;
};

const WARNING_MESSAGE = "Attenzione: decisione vincolante";

/**
 * Detects binding decision conflict with active entity/selection for ContextBar amber state.
 * Integration A wires the returned state into ContextBar.
 */
export function computeDecisionWarning(
  input: UseDecisionWarningInput
): DecisionWarningState {
  const decisions = input.packet ? parseDecisionsFromPacket(input.packet) : [];
  const entity = input.entity ?? input.packet?.entity ?? null;
  const conflict = findConflictingDecision(decisions, entity, input.selectionText);

  if (!conflict) {
    return { active: false, message: null };
  }

  return {
    active: true,
    message: WARNING_MESSAGE,
    decisionId: conflict.id,
    decision: conflict,
  };
}

export function useDecisionWarning(input: UseDecisionWarningInput): DecisionWarningState {
  const { packet, entity, selectionText } = input;

  return useMemo(
    () => computeDecisionWarning({ packet, entity, selectionText }),
    [packet, entity, selectionText]
  );
}
